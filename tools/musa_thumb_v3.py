#!/usr/bin/env python3
"""Thumbnail Musa 14 v3: series template (assets/thumbnails/boa_folge14_thumbnail_serie.jpg) with the
right panel taken from the sea picture used in the video (sea_split_ohne_spuren – no footprints),
title 'Das Meer teilt sich' + 'MUSA' redrawn in the series style."""
import json, os, urllib.request
def get(u, dst):
    r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
    open(dst, "wb").write(urllib.request.urlopen(r, timeout=120).read())
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "out", "folge14_musa_v3"); os.makedirs(out, exist_ok=True)
base = Image.open(os.path.join(ROOT, "assets/thumbnails/boa_folge14_thumbnail_serie.jpg")).convert("RGB")
W, H = base.size  # 1280x720
url = next(s["image"] for s in json.load(open(os.path.join(ROOT, "jobs/folge14_musa_v2.json")))["segments"]
           if "sea_split_ohne_spuren" in s["image"])
src = "/tmp/sea.jpg"
get(url, src)
sea = Image.open(src).convert("RGB")
# right panel: from the slanted divider (x≈806 at top, ≈746 at bottom) to the right edge
pw = W - 740
r = max(pw / sea.width, H / sea.height)
sea = sea.resize((int(sea.width * r) + 1, int(sea.height * r) + 1), Image.LANCZOS)
cx = (sea.width - pw) // 2
panel = sea.crop((cx, 0, cx + pw, H))
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).polygon([(812, 0), (W, 0), (W, H), (752, H)], fill=255)
layer = Image.new("RGB", (W, H)); layer.paste(panel, (740, 0))
img = Image.composite(layer, base, mask.filter(ImageFilter.GaussianBlur(1.2)))
d = ImageDraw.Draw(img)
d.line([(809, 0), (749, H)], fill=(250, 240, 220), width=5)  # cream divider like the template
fp = "/tmp/pop.ttf"
get("https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-ExtraBold.ttf", fp)
def center_text(txt, size, y, fill, stroke, sw, shadow=None):
    f = ImageFont.truetype(fp, size)
    while True:
        bb = d.textbbox((0, 0), txt, font=f, stroke_width=sw)
        if bb[2] - bb[0] <= 470 or size < 30: break
        size -= 2; f = ImageFont.truetype(fp, size)
    x = 1012 - (bb[2] - bb[0]) // 2 - bb[0]
    if shadow:
        d.text((x + 6, y + 7), txt, font=f, fill=shadow, stroke_width=sw, stroke_fill=shadow)
    d.text((x, y), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
center_text("Das Meer teilt sich", 44, 383, (255, 255, 255), (40, 22, 52), 5)
center_text("MUSA", 118, 455, (255, 226, 52), (40, 22, 52), 6, shadow=(40, 22, 52))
p = os.path.join(out, "thumb_musa_v3.jpg")
img.save(p, quality=93)
print("saved", p, img.size)
