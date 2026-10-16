#!/usr/bin/env python3
"""Check sheets for new images (free, no Orshot credits).

jobs/sheets/<name>.json: {"name": "...", "images": [{"label": "...", "url": "https://..."}, ...], "cols": 3}
-> out/sheets/<name>.jpg  (each image 640x360 with its label; full-size crops are not needed for a first look)
-> out/sheets/<name>_big/<label>.jpg  (each image at 1280 width, for zoom checks)
"""
import glob
import hashlib
import json
import os
import subprocess
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "sheets")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main():
    os.makedirs(OUT, exist_ok=True)
    for jf in sorted(glob.glob(os.path.join(ROOT, "jobs", "sheets", "*.json"))):
        raw = open(jf, "rb").read()
        h = hashlib.sha1(raw).hexdigest()
        job = json.loads(raw)
        name = job["name"]
        stamp = os.path.join(OUT, name + ".hash")
        if os.path.exists(stamp) and open(stamp).read().strip() == h:
            continue
        tmp = os.path.join("/tmp", "sheet_" + name)
        big = os.path.join(OUT, name + "_big")
        os.makedirs(tmp, exist_ok=True)
        os.makedirs(big, exist_ok=True)
        cols = int(job.get("cols", 3))
        imgs = job["images"]
        rows = -(-len(imgs) // cols)
        for k in range(rows * cols):
            dest = os.path.join(tmp, f"{k:03d}.jpg")
            if k < len(imgs):
                it = imgs[k]
                src = os.path.join(tmp, f"src{k:03d}")
                req = urllib.request.Request(it["url"], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
                with urllib.request.urlopen(req, timeout=120) as r, open(src, "wb") as f:
                    f.write(r.read())
                label = it["label"].replace(":", " ").replace("'", "")
                run(["ffmpeg", "-y", "-i", src, "-vf",
                     "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,"
                     f"drawtext=fontfile={FONT}:text='{k + 1} {label}':x=6:y=6:fontsize=20:"
                     "fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=4,format=yuvj420p", "-q:v", "3", dest])
                run(["ffmpeg", "-y", "-i", src, "-vf", "scale=1280:-2", "-q:v", "3",
                     os.path.join(big, f"{k + 1:02d}_{it['label']}.jpg")])
                if job.get("keep_original"):
                    import shutil
                    shutil.copy(src, os.path.join(big, f"{k + 1:02d}_{it['label']}_original.jpg"))
            else:
                run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=640x360", "-vf", "format=yuvj420p",
                     "-frames:v", "1", dest])
        run(["ffmpeg", "-y", "-framerate", "1", "-i", os.path.join(tmp, "%03d.jpg"), "-vf",
             f"tile={cols}x{rows}:padding=4", "-frames:v", "1", "-q:v", "3",
             os.path.join(OUT, name + ".jpg")])
        open(stamp, "w").write(h)
        print("sheet", name, len(imgs))


if __name__ == "__main__":
    main()
