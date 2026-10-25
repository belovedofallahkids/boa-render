#!/usr/bin/env python3
import subprocess, urllib.request, os
u = "https://github.com/belovedofallahkids/boa-render/releases/download/folge03_nuh_v2/folge03_nuh_v2.mp4"
urllib.request.urlretrieve(u, "/tmp/v2.mp4")
os.makedirs("out/nuh_fix/replace", exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "30", "-to", "126", "-i", "/tmp/v2.mp4",
                "-vf", "fps=1,scale=320:-1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\\:hms\\:30}':x=5:y=5:fontsize=20:fontcolor=yellow:box=1:boxcolor=black,tile=8x12",
                "-frames:v", "1", "out/nuh_fix/replace/sec_30_126.jpg"], check=True)
