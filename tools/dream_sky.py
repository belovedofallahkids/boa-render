#!/usr/bin/env python3
"""Folge 10 – Yusufs Traum (Sure 12:4): genau 11 Sterne, die Sonne und der Mond.

Die KI zaehlt Sterne nicht zuverlaessig (dream_sky 48963 hatte 8 Sterne und 2 Monde).
Darum: leerer Traumhimmel (dream_sky_bg 48969) + Himmelskoerper hier gezeichnet,
weich und rund im Serienstil, ohne Gesichter.

Aufruf: python3 tools/dream_sky.py <hintergrund.jpg> <ausgabe.png>
"""
import math
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

SS = 3  # Supersampling fuer weiche Kanten


def star_points(cx, cy, r_out, r_in, rot=-90.0):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def glow(size, draw_fn, blur, strength=1.0):
    """Helligkeitsmaske einer Form, weichgezeichnet."""
    m = Image.new("L", size, 0)
    draw_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    if strength != 1.0:
        m = m.point(lambda v: min(255, int(v * strength)))
    return m


def add_light(base, mask, color):
    layer = Image.new("RGB", base.size, color)
    return Image.composite(layer, base, mask)


def screen_light(base, mask, color):
    layer = Image.new("RGB", base.size, (0, 0, 0))
    layer = Image.composite(Image.new("RGB", base.size, color), layer, mask)
    return ImageChops.screen(base, layer)


def main(src, dst):
    bg = Image.open(src).convert("RGB")
    W0, H0 = bg.size
    W, H = W0 * SS, H0 * SS
    img = bg.resize((W, H), Image.LANCZOS)
    u = W / 1536.0  # Masseinheit relativ zur Normalbreite

    # 11 Sterne im hohen Bogen, Sonne und Mond an den beiden Fuessen des Bogens.
    # (Nicht Sonne+Mond oben und Sterne darunter: das saehe wie ein Gesicht aus.)
    # Mond auf der blauen Nachtseite (links), Sonne auf der goldenen Tagseite (rechts)
    moon = (W * 0.14, H * 0.40, 56 * u)
    sun = (W * 0.86, H * 0.45, 64 * u)
    cx, cy, rx, ry = W * 0.5, H * 0.62, W * 0.33, H * 0.48
    stars = []
    for i in range(11):
        a = math.radians(152 - i * 12.4)
        stars.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))

    # Sonne: breiter warmer Schein, dann Scheibe
    sx, sy, sr = sun
    img = screen_light(img, glow((W, H), lambda d: d.ellipse([sx - sr * 2.4, sy - sr * 2.4, sx + sr * 2.4, sy + sr * 2.4], fill=150), 60 * u), (255, 190, 90))
    img = screen_light(img, glow((W, H), lambda d: d.ellipse([sx - sr * 1.35, sy - sr * 1.35, sx + sr * 1.35, sy + sr * 1.35], fill=220), 22 * u), (255, 214, 120))
    disc = glow((W, H), lambda d: d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=255), 1.5 * u)
    img = add_light(img, disc, (255, 205, 95))
    core = glow((W, H), lambda d: d.ellipse([sx - sr * 0.78, sy - sr * 0.86, sx + sr * 0.62, sy + sr * 0.5], fill=200), 18 * u)
    img = screen_light(img, core, (255, 240, 190))

    # Mond: Sichel = Scheibe minus versetzte Scheibe
    mx, my, mr = moon
    img = screen_light(img, glow((W, H), lambda d: d.ellipse([mx - mr * 2.0, my - mr * 2.0, mx + mr * 2.0, my + mr * 2.0], fill=110), 50 * u), (200, 215, 255))
    m_full = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m_full).ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=255)
    m_cut = Image.new("L", (W, H), 0)
    off = mr * 0.55
    ImageDraw.Draw(m_cut).ellipse([mx - mr + off, my - mr - off * 0.35, mx + mr + off, my + mr - off * 0.35], fill=255)
    crescent = ImageChops.subtract(m_full, m_cut).filter(ImageFilter.GaussianBlur(1.5 * u))
    img = screen_light(img, crescent.filter(ImageFilter.GaussianBlur(14 * u)), (255, 240, 200))
    img = add_light(img, crescent, (255, 236, 170))

    # 11 Sterne: weicher Schein + runde Fuenfzack-Form
    for (x, y) in stars:
        r = 26 * u
        img = screen_light(img, glow((W, H), lambda d, x=x, y=y: d.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2], fill=120), 26 * u), (255, 220, 140))
        rim = Image.new("L", (W, H), 0)
        ImageDraw.Draw(rim).polygon(star_points(x, y, r * 1.18, r * 0.62), fill=255)
        rim = rim.filter(ImageFilter.GaussianBlur(4 * u)).point(lambda v: min(255, int(v * 1.6)))
        img = add_light(img, rim, (236, 150, 60))  # warmer Rand, damit Sterne auch auf hellem Himmel stehen
        shape = Image.new("L", (W, H), 0)
        ImageDraw.Draw(shape).polygon(star_points(x, y, r, r * 0.5), fill=255)
        shape = shape.filter(ImageFilter.GaussianBlur(3.2 * u))  # rundet die Spitzen ab
        shape = shape.point(lambda v: 255 if v > 110 else int(v * 255 / 110))
        img = add_light(img, shape, (255, 222, 120))
        hi = glow((W, H), lambda d, x=x, y=y: d.ellipse([x - r * 0.35, y - r * 0.45, x + r * 0.15, y + r * 0.05], fill=200), 4 * u)
        img = screen_light(img, hi, (255, 250, 225))

    img.resize((W0, H0), Image.LANCZOS).save(dst)
    print("ok", dst, W0, H0, "Sterne:", len(stars))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
