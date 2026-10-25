#!/usr/bin/env python3
"""Thumbnail Folge 03: replace the word 'NUH' by 'NOAH' (owner 25.10.2026: prophet named like the child)."""
import urllib.request, numpy as np, cv2, os
from PIL import Image, ImageDraw, ImageFont
o = "out/nuh_fix/thumb"; os.makedirs(o, exist_ok=True)
urllib.request.urlretrieve("https://i.ytimg.com/vi/KRlC8t0bHcA/maxresdefault.jpg", f"{o}/orig.jpg")
urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-ExtraBold.ttf", "/tmp/pop.ttf")
im = cv2.imread(f"{o}/orig.jpg"); h, w = im.shape[:2]
# exact box of the word NUH (measured on the 1280x720 original): letters 930-1230 x 470-575 incl. outline
x0, y0, x1, y1 = 936, 476, 1226, 572
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
yel = np.zeros((h, w), bool); sub = cv2.inRange(hsv[y0:y1, x0:x1], (18, 150, 200), (40, 255, 255)) > 0
yel[y0:y1, x0:x1] = sub
open(f"{o}/bbox.txt", "w").write(f"{x0} {y0} {x1} {y1}\n")
pad = 12
mask = np.zeros((h, w), np.uint8); mask[452:604, 908:1250] = 255
clean = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
pil = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(pil)
# sample letter colour
col = tuple(int(c) for c in np.median(im[yel > 0], axis=0)[::-1])
target_h = y1 - y0
size = int(target_h * 1.36)
font = ImageFont.truetype("/tmp/pop.ttf", size)
txt = "NOAH"
while True:
    bb = d.textbbox((0, 0), txt, font=font, stroke_width=6)
    if bb[2] - bb[0] <= 470 or size < 40: break
    size -= 4; font = ImageFont.truetype("/tmp/pop.ttf", size)
bb = d.textbbox((0, 0), txt, font=font, stroke_width=7)
X = 1236 - bb[2]             # right edge like the original word (incl. outline)
Y = 584 - bb[3]              # bottom edge like the original word (incl. outline)
d.text((X, Y), txt, font=font, fill=col, stroke_width=7, stroke_fill=(38, 18, 48))
pil.save(f"{o}/thumb_noah.jpg", quality=92)
print("bbox", x0, y0, x1, y1, "color", col, "size", size)
