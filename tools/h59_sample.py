"""H59 sample (owner 31.10.2026): more movement, same approved images.

Takes a ~60 s window of a published episode job and re-renders it:
- every long image is split into camera shots of ~4-6 s (zoom / pan / tilt
  between crops of at most 1.28x, so the motif always stays in frame),
- soft crossfades between shots,
- light procedural motion layers by scene (golden dust, light rays, embers,
  twinkling stars) - dots and light only, never shapes,
- speaking-child images keep one gentle zoom (H9) and get no overlay.
No new images, no music. Output: after.mp4, before.mp4 (same window from the
published file) and a contact sheet for the zoom check (H35/H36).

Env: JOB (jobs/<name>.json), VIDEO_URL (published render), T0, T1.
"""
import json, math, os, random, subprocess, sys, urllib.request

import cv2
import numpy as np

W, H, FPS = 1920, 1080, 30
XF = 0.7          # crossfade between shots (s)
SHOT = 5.0        # target shot length (s)
ZMAX = 1.28
OUT = "out/h59_sample"
os.makedirs(OUT, exist_ok=True)
random.seed(59)
np.random.seed(59)


def fetch(url, cache={}):
    if url in cache:
        return cache[url]
    p = os.path.join(OUT, "img_" + str(len(cache)) + os.path.splitext(url.split("?")[0])[1])
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    open(p, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    im = cv2.imread(p, cv2.IMREAD_COLOR)
    # cover 16:9 at 2x output size
    h, w = im.shape[:2]
    s = max(2 * W / w, 2 * H / h)
    im = cv2.resize(im, (int(w * s + 0.5), int(h * s + 0.5)), interpolation=cv2.INTER_LANCZOS4)
    h, w = im.shape[:2]
    y0, x0 = (h - 2 * H) // 2, (w - 2 * W) // 2
    im = im[y0:y0 + 2 * H, x0:x0 + 2 * W].astype(np.float32)
    cache[url] = im
    return im


def rect(z, ax, ay):
    """crop rect (cx, cy, scale) for zoom z, anchor ax/ay in [-1,1] of free room"""
    fw, fh = 1 / z, 1 / z
    cx = 0.5 + ax * (1 - fw) / 2
    cy = 0.5 + ay * (1 - fh) / 2
    return np.array([cx, cy, z])


MOVES = [  # (start rect, end rect)
    (rect(1.00, 0, 0), rect(1.22, 0, -0.2)),      # push in
    (rect(1.25, -1, 0), rect(1.25, 1, 0)),        # pan right
    (rect(1.25, 0, -1), rect(1.18, 0, 0.6)),      # tilt down
    (rect(1.26, 0.6, 0.2), rect(1.02, 0, 0)),     # pull out
    (rect(1.24, 1, -0.3), rect(1.24, -1, 0.2)),   # pan left
    (rect(1.05, -0.3, 0), rect(1.28, 0.4, -0.4)), # push in to detail
]


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))


def view(src, r):
    cx, cy, z = r
    sh, sw = src.shape[:2]
    cw, ch = sw / z, sh / z
    x0, y0 = cx * sw - cw / 2, cy * sh - ch / 2
    sx, sy = W / cw, H / ch
    M = np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_AREA if sx < 0.6 else cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)


def kind(url):
    u = url.lower()
    if "allein" in u or "schlafen" in u or "oma_" in u or "master_a" in u:
        return "child"
    if "fire" in u:
        return "embers"
    if "night" in u or "sky" in u or "star" in u:
        return "stars"
    if "light" in u or "glow" in u or "sunrise" in u or "valley" in u or "staff" in u:
        return "rays"
    return "dust"


# ---------- procedural layers (half resolution, then upscaled) ----------
HW, HH = W // 2, H // 2
yy, xx = np.mgrid[0:HH, 0:HW].astype(np.float32)
vign = 1 - 0.28 * (((xx - HW / 2) / (HW / 2)) ** 2 + ((yy - HH / 2) / (HH / 2)) ** 2) / 2
vign = cv2.resize(vign, (W, H))[..., None]
ang = np.arctan2(yy + HH * 0.35, xx - HW * 0.5)
dist = np.sqrt((xx - HW * 0.5) ** 2 + (yy + HH * 0.35) ** 2)


class Particles:
    def __init__(self, n, kind):
        self.k = kind
        self.p = np.random.rand(n, 2) * [HW, HH]
        self.v = np.random.randn(n, 2) * 3
        self.r = np.random.uniform(1.0, 2.6, n)
        self.ph = np.random.rand(n) * 6.28
        if kind == "embers":
            self.v = np.c_[np.random.randn(n) * 6, -np.random.uniform(12, 30, n)]
            self.p[:, 1] = np.random.uniform(HH * 0.4, HH, n)

    def frame(self, t, dt):
        lay = np.zeros((HH, HW, 3), np.float32)
        self.p += self.v * dt + np.c_[np.sin(t * 0.7 + self.ph) * 0.4, np.cos(t * 0.5 + self.ph) * 0.2]
        if self.k == "embers":
            dead = self.p[:, 1] < HH * 0.25
            self.p[dead] = np.c_[np.random.rand(dead.sum()) * HW, np.full(dead.sum(), HH * 1.02)]
        self.p %= [HW, HH]
        col = {"embers": (60, 150, 255), "stars": (255, 245, 230)}.get(self.k, (150, 215, 255))
        tw = 0.5 + 0.5 * np.sin(t * 2.3 + self.ph * 3)
        for (x, y), r, a in zip(self.p, self.r, tw):
            c = tuple(float(v) * (0.35 + 0.65 * a) for v in col)
            cv2.circle(lay, (int(x), int(y)), int(r + 0.5), c, -1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 1.6) + cv2.GaussianBlur(lay, (0, 0), 5) * 0.8
        return lay


def rays(t):
    s = 0.5 + 0.5 * np.sin(ang * 22 + t * 0.35) * np.sin(ang * 9 - t * 0.21)
    a = np.clip(s, 0, 1) ** 3 * np.exp(-dist / (HH * 1.4)) * (0.55 + 0.15 * math.sin(t * 0.8))
    return np.dstack([a * 150, a * 215, a * 255])


def main():
    job = json.load(open(os.environ["JOB"]))
    t0, t1 = float(os.environ["T0"]), float(os.environ["T1"])
    segs = []
    for s in job["segments"]:
        a, b = s["start"], s.get("end")
        b = b if isinstance(b, (int, float)) else 1e9
        if b <= t0 or a >= t1 or s.get("disabled"):
            continue
        segs.append((max(a, t0) - t0, min(b, t1) - t0, s["image"]))
    # build shots
    shots, mi = [], 0
    for a, b, url in segs:
        k = kind(url)
        if k == "child" or b - a < 6:
            shots.append((a, b, url, (rect(1.0, 0, 0), rect(1.06, 0, -0.1)), k))
            continue
        n = max(1, round((b - a) / SHOT))
        L = (b - a) / n
        for i in range(n):
            shots.append((a + i * L, a + (i + 1) * L, url, MOVES[mi % len(MOVES)], k))
            mi += 1
    json.dump([(round(a, 2), round(b, 2), u.split("/")[-1], k) for a, b, u, _, k in shots],
              open(f"{OUT}/shots.json", "w"), indent=1)

    total = t1 - t0
    nfr = int(round(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", f"{OUT}/video.mp4"], stdin=subprocess.PIPE)
    parts = {}

    def shot_frame(i, t):
        a, b, url, (r0, r1), k = shots[i]
        u = (t - a + XF / 2) / (b - a + XF)
        img = view(fetch(url), r0 + (r1 - r0) * ease(u))
        if k != "child":
            if k not in parts:
                parts[k] = Particles({"embers": 70, "stars": 120}.get(k, 90), k)
            lay = parts[k].frame(t, 1 / FPS)
            if k == "rays":
                lay = lay + rays(t)
            img = img + cv2.resize(lay, (W, H)) * 0.55
            img = img * vign
        return img

    for f in range(nfr):
        t = f / FPS
        i = max(j for j in range(len(shots)) if shots[j][0] <= t + 1e-6)
        fr = shot_frame(i, t)
        if i + 1 < len(shots) and t > shots[i][1] - XF / 2:
            w = ease((t - (shots[i][1] - XF / 2)) / XF)
            fr = fr * (1 - w) + shot_frame(i + 1, t) * w
        fade = min(1, t / 0.6, (total - t) / 0.8)
        ff.stdin.write(np.clip(fr * fade, 0, 255).astype(np.uint8).tobytes())
        if f % 300 == 0:
            print("frame", f, "/", nfr, flush=True)
    ff.stdin.close()
    ff.wait()

    sh = lambda c: subprocess.run(c, check=True)
    au = os.environ.get("VIDEO_URL") or job["audio"]  # published file = already -14 LUFS
    sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t0), "-t", str(total), "-i", au,
        "-vn", "-af", f"afade=t=in:d=0.4,afade=t=out:st={total-0.8}:d=0.8", f"{OUT}/audio.wav"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/video.mp4", "-i", f"{OUT}/audio.wav",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        f"{OUT}/h59_after.mp4"])
    if os.environ.get("VIDEO_URL"):
        sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t0), "-t", str(total), "-i", os.environ["VIDEO_URL"],
            "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-movflags", "+faststart", f"{OUT}/h59_before.mp4"])
    # contact sheet: one frame every 2 s, plus full frames per shot middle for zoom check
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/h59_after.mp4", "-vf",
        "fps=1/2,scale=480:270,tile=6x5", "-frames:v", "1", f"{OUT}/contact.jpg"])
    os.makedirs(f"{OUT}/frames", exist_ok=True)
    for n, (a, b, *_rest) in enumerate(shots):
        for tag, tt in (("a", a + 0.8), ("m", (a + b) / 2), ("b", b - 0.8)):
            sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(tt,0):.2f}", "-i", f"{OUT}/h59_after.mp4",
                "-frames:v", "1", "-q:v", "3", f"{OUT}/frames/shot{n:02d}_{tag}.jpg"])
    print("done", len(shots), "shots")


if __name__ == "__main__":
    main()
