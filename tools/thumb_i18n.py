#!/usr/bin/env python3
"""Localized series thumbnail (owner 13.11.2026: one thumbnail per audio language, YouTube Studio > Langues > Miniature).
Same layout as tools/thumb_serie.py (template 26008); also re-draws the white top label in the target language.
Usage: thumb_i18n.py <base_26008_render.jpg> <scene_image> <lang> "<label>" "<subtitle>" "<NAME>" <out.jpg>
Arabic (lang=ar) uses Noto Kufi Arabic with RTL shaping (Pillow + raqm)."""
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import thumb_serie as ts

def font(lang, latin, size):
    if lang == "ar":
        f = ImageFont.truetype(ts.FONTS + "NotoKufiArabic.ttf", size, layout_engine=ImageFont.Layout.RAQM)
        f.set_variation_by_name("Black" if "Black" in latin else "ExtraBold")
        return f
    return ImageFont.truetype(ts.FONTS + latin, size)

def kw(lang):
    return {"direction": "rtl", "language": "ar"} if lang == "ar" else {}

def fit(lang, latin, size, text, maxw):
    f = font(lang, latin, size)
    while size > 20 and f.getbbox(text, **kw(lang))[2] - f.getbbox(text, **kw(lang))[0] > maxw:
        size -= 2
        f = font(lang, latin, size)
    return f

def center(canvas, text, f, cx, cy, fill, lang, outline=0, shadow=None):
    d = ImageDraw.Draw(canvas)
    if shadow:
        d.text((cx + shadow[0], cy + shadow[1]), text, font=f, fill=ts.PLUM, anchor="mm", stroke_width=outline, stroke_fill=ts.PLUM, **kw(lang))
    d.text((cx, cy), text, font=f, fill=fill, anchor="mm", stroke_width=outline, stroke_fill=ts.PLUM, **kw(lang))

def main(base, scene, lang, label, subtitle, name, out):
    W, H = ts.W, ts.H
    b = Image.open(base).convert("RGB").resize((W, H))
    left = int(ts.X_BOT) - 4
    panel = ts.cover(Image.open(scene).convert("RGB"), W - left, H)
    canvas = Image.new("RGB", (W, H)); canvas.paste(panel, (left, 0))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(0, 0), (ts.X_TOP, 0), (ts.X_BOT, H), (0, H)], fill=255)
    canvas.paste(b, (0, 0), mask)
    d = ImageDraw.Draw(canvas)
    for y in range(H):
        x = ts.divider_x(y); d.line([(x - 2.0, y), (x + 2.0, y)], fill=ts.CREAM)
    # top label: clean white pill, localized text
    fl = fit(lang, "Poppins-Bold.ttf", 26 if lang != "ar" else 27, label, 500)
    tw = fl.getbbox(label, **kw(lang))[2] - fl.getbbox(label, **kw(lang))[0]
    pw = max(543, tw + 64)
    d.rounded_rectangle([17, 14, 17 + pw, 65], radius=26, fill=(255, 255, 255))
    center(canvas, label, fl, 17 + pw / 2, 39 if lang != "ar" else 37, (74, 34, 70), lang)
    cx = 1011.5
    fs = fit(lang, "Poppins-ExtraBold.ttf", 46 if lang != "ar" else 50, subtitle, 470)
    fn = fit(lang, "Poppins-Black.ttf", 117 if lang != "ar" else 112, name, 470)
    center(canvas, subtitle, fs, cx, 416 if lang != "ar" else 404, (255, 255, 255), lang, outline=3, shadow=(2, 3))
    center(canvas, name, fn, cx, 548 if lang != "ar" else 540, ts.YELLOW, lang, outline=3, shadow=(0, 7))
    canvas.save(out, quality=92)

if __name__ == "__main__":
    main(*sys.argv[1:8])
