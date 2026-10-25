#!/usr/bin/env python3
import subprocess, urllib.request, os
u = "https://github.com/belovedofallahkids/boa-render/releases/download/folge03_nuh_v2/folge03_nuh_v2.mp4"
urllib.request.urlretrieve(u, "/tmp/v2.mp4")
o = "out/nuh_fix/replace/check2"; os.makedirs(o, exist_ok=True)
for t in (165, 168, 170, 172, 175):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", "/tmp/v2.mp4", "-frames:v", "1", "-q:v", "2", f"{o}/full_{t}.jpg"], check=True)
# every second of the whole video, tiled 10x7 per sheet (70 s per sheet), 240 px wide
for k, s in enumerate(range(0, 345, 70)):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(s), "-t", "70", "-i", "/tmp/v2.mp4", "-vf",
                    "fps=1,scale=240:-1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\\:hms\\:" + str(s) + "}':x=3:y=3:fontsize=14:fontcolor=yellow:box=1:boxcolor=black,tile=10x7",
                    "-frames:v", "1", f"{o}/sec_sheet_{k}.jpg"], check=True)
