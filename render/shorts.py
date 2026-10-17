#!/usr/bin/env python3
"""Vertical Shorts (1080x1920) from a finished episode video. Free (GitHub Actions + ffmpeg).
jobs/shorts/<name>.json: {"name": "...", "video": "https://.../folgeNN.mp4",
  "clips": [{"id": "s1", "start": 185.4, "end": 233.2, "title": "Das goldene Kalb", "top": "Prophet Harun"}]}
Layout: blurred full-screen background, the 16:9 video in the middle, white title above,
'Ganze Geschichte auf dem Kanal' below. Soft fade in/out.
-> release shorts_<name>: <name>_<id>.mp4 ; status out/shorts/<name>/status.json"""
import glob, hashlib, json, os, subprocess, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "belovedofallahkids/boa-render")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def run(c):
    subprocess.run(c, check=True)

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")

def main():
    for jf in sorted(glob.glob(os.path.join(ROOT, "jobs", "shorts", "*.json"))):
        raw = open(jf, "rb").read(); h = hashlib.sha1(raw).hexdigest(); job = json.loads(raw)
        name = job["name"]; od = os.path.join(ROOT, "out", "shorts", name); st = os.path.join(od, "status.json")
        if os.path.exists(st) and json.load(open(st)).get("hash") == h:
            continue
        os.makedirs(od, exist_ok=True)
        wd = "/tmp/shorts_" + name; os.makedirs(wd, exist_ok=True)
        src = os.path.join(wd, "src.mp4")
        req = urllib.request.Request(job["video"], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
        with urllib.request.urlopen(req, timeout=600) as r, open(src, "wb") as f:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
        files = []
        for c in job["clips"]:
            d = c["end"] - c["start"]
            out = os.path.join(wd, f"{name}_{c['id']}.mp4")
            top = esc(c.get("top", "")); title = esc(c["title"]); bottom = esc(c.get("bottom", "Die ganze Geschichte auf unserem Kanal"))
            vf = (f"[0:v]split=2[a][b];"
                  f"[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.15[bg];"
                  f"[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2,"
                  f"drawtext=fontfile={FONT}:text='{top}':fontcolor=0xFFD54A:fontsize=58:borderw=4:bordercolor=0x2b1a4a:x=(w-text_w)/2:y=330,"
                  f"drawtext=fontfile={FONT}:text='{title}':fontcolor=white:fontsize=72:borderw=5:bordercolor=0x2b1a4a:x=(w-text_w)/2:y=420,"
                  f"drawtext=fontfile={FONT}:text='{bottom}':fontcolor=white:fontsize=44:borderw=3:bordercolor=0x2b1a4a:x=(w-text_w)/2:y=1520,"
                  f"fade=t=in:st=0:d=0.5,fade=t=out:st={d-0.8:.2f}:d=0.8[v]")
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(c["start"]), "-t", f"{d:.2f}", "-i", src,
                 "-filter_complex", vf, "-map", "[v]", "-map", "0:a",
                 "-af", f"afade=t=in:st=0:d=0.4,afade=t=out:st={d-0.8:.2f}:d=0.8",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
                 "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
            files.append(out)
        tag = "shorts_" + name
        ex = subprocess.run(["gh", "release", "view", tag, "--repo", REPO], capture_output=True).returncode == 0
        if ex:
            run(["gh", "release", "upload", tag, *files, "--clobber", "--repo", REPO])
        else:
            run(["gh", "release", "create", tag, *files, "--repo", REPO, "--title", tag, "--notes", "Shorts (automatisch, kostenlos)"])
        json.dump({"hash": h, "ok": True, "urls": {os.path.basename(f): f"https://github.com/{REPO}/releases/download/{tag}/{os.path.basename(f)}" for f in files}},
                  open(st, "w"), indent=1)

if __name__ == "__main__":
    main()
