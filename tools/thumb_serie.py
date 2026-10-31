#!/usr/bin/env python3
"""Series thumbnail in the exact layout of Orshot template 26008 (1280x720).

The left panel (characters + white label) is taken pixel-for-pixel from an existing
26008 render, so only the right panel (scene, subtitle, prophet name) changes.
Usage: thumb_serie.py <base_26008_render.jpg> <scene_image> "<subtitle>" "<NAME>" <out.jpg>
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
X_TOP, X_BOT = 808.5, 742.5          # cream divider: x at y=0 and y=719 (measured on 26008 renders)
CREAM = (250, 243, 226)
YELLOW = (255, 225, 74)
PLUM = (44, 16, 46)
FONTS = "assets/fonts/"


def divider_x(y):
    return X_TOP + (X_BOT - X_TOP) * y / (H - 1)


def cover(img, w, h, cx=0.5):
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0 = int((img.width - w) * cx)
    y0 = (img.height - h) // 2
    return img.crop((x0, y0, x0 + w, y0 + h))


def text_center(draw_base, text, font, cx, top, fill, outline=0, shadow=(0, 0), shadow_blur=0):
    b = font.getbbox(text)
    x = cx - (b[2] - b[0]) / 2 - b[0]
    y = top - b[1]
    if shadow != (0, 0) or shadow_blur:
        sh = Image.new("RGBA", draw_base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        d.text((x + shadow[0], y + shadow[1]), text, font=font, fill=PLUM + (235,),
               stroke_width=outline, stroke_fill=PLUM + (235,))
        if shadow_blur:
            sh = sh.filter(ImageFilter.GaussianBlur(shadow_blur))
        draw_base.alpha_composite(sh)
    d = ImageDraw.Draw(draw_base)
    d.text((x, y), text, font=font, fill=fill, stroke_width=outline, stroke_fill=PLUM)


def main(base, scene, subtitle, name, out):
    base = Image.open(base).convert("RGB").resize((W, H))
    left = int(X_BOT) - 4
    panel = cover(Image.open(scene).convert("RGB"), W - left, H)
    canvas = Image.new("RGB", (W, H))
    canvas.paste(panel, (left, 0))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(0, 0), (X_TOP, 0), (X_BOT, H), (0, H)], fill=255)
    canvas.paste(base, (0, 0), mask)
    d = ImageDraw.Draw(canvas)
    for y in range(H):
        x = divider_x(y)
        d.line([(x - 2.0, y), (x + 2.0, y)], fill=CREAM)
    canvas = canvas.convert("RGBA")
    cx = 1011.5
    f_sub = ImageFont.truetype(FONTS + "Poppins-ExtraBold.ttf", 46)
    f_name = ImageFont.truetype(FONTS + "Poppins-Black.ttf", 117)
    text_center(canvas, subtitle, f_sub, cx, 390, (255, 255, 255), shadow=(2, 3), shadow_blur=3)
    text_center(canvas, name, f_name, cx, 482, YELLOW, outline=2, shadow=(0, 7))
    canvas.convert("RGB").save(out, quality=92)


if __name__ == "__main__":
    main(*sys.argv[1:6])
