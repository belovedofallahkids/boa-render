#!/usr/bin/env python3
"""Motion library (free, CPU, H59 + owner 15.11.2026 «no static pictures»): every picture of an
episode becomes ready-made 2.5D camera clips (Depth-Anything parallax, tools/parallax.py), so on
production day every shot already moves. Sources: prompts/h59_<EP>.json (images with a file) and/or
jobs/motion/<EP>.json {"images": {"name": "url or repo path"}}. Output: /tmp/motion/<name>__<move>.mp4
(1920x1080, 30 fps, 8 s, no audio). Already-built clips listed in /tmp/have.txt are skipped."""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parallax
EP = os.environ["EP"]; MOVES = os.environ.get("MOVES", "zoom_in,pan_right,pan_left").split(",")
LEN = float(os.environ.get("LEN", "8"))
os.makedirs("/tmp/motion", exist_ok=True); os.makedirs("/tmp/src", exist_ok=True)
have = set(open("/tmp/have.txt").read().split()) if os.path.exists("/tmp/have.txt") else set()
src = {}
p = f"prompts/h59_{EP}.json"
if os.path.exists(p):
    for im in json.load(open(p))["images"]:
        if im.get("file") and os.path.exists(im["file"]) and im.get("status") != "rejected":
            src[im["id"]] = im["file"]
m = f"jobs/motion/{EP}.json"
if os.path.exists(m):
    src.update(json.load(open(m))["images"])
print("images", len(src), flush=True)
done = 0
for name, s in src.items():
    f = s
    if s.startswith("http"):
        f = f"/tmp/src/{name}.img"
        if not os.path.exists(f):
            urllib.request.urlretrieve(s, f)
    for mv in MOVES:
        out = f"/tmp/motion/{name}__{mv}.mp4"
        if os.path.basename(out) in have:
            continue
        parallax.render_clip(0, {"motion": mv, "parallax": 26.0}, f, LEN, 30, out)
        done += 1; print("ok", os.path.basename(out), flush=True)
print("built", done)
