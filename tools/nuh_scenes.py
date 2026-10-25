#!/usr/bin/env python3
import json, subprocess, urllib.request
u = "https://github.com/belovedofallahkids/boa-render/releases/download/folge03_nuh_v2/folge03_nuh_v2.mp4"
urllib.request.urlretrieve(u, "/tmp/v2.mp4")
r = subprocess.run(["ffmpeg", "-i", "/tmp/v2.mp4", "-vf", "select='gt(scene,0.08)',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True)
ts = [float(l.split("pts_time:")[1].split()[0]) for l in r.stderr.splitlines() if "pts_time:" in l]
import os; os.makedirs("out/nuh_fix/replace/scenes", exist_ok=True)
for i, t in enumerate(ts):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t + 0.5), "-i", "/tmp/v2.mp4", "-frames:v", "1", "-vf", "scale=480:-1",
                    f"out/nuh_fix/replace/scenes/s_{i:02d}_{t:07.2f}.jpg"])
json.dump(ts, open("out/nuh_fix/replace/scenes.json", "w"))
print(ts)
