#!/usr/bin/env python3
"""Align published waveform (YouTube Studio editor data, max-min per 12 ms) with Orshot audio 260,
then test the editor cut (published times) mapped into 260 time."""
import json, subprocess, urllib.request
import numpy as np
URL = "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge03_nuh_alt_ton_mit_schrittenm4a-K5ddGJhffjV.m4a"
src = "/tmp/nuh260.m4a"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
with urllib.request.urlopen(req, timeout=300) as r, open(src, "wb") as f:
    f.write(r.read())
P = json.load(open("out/nuh_fix/published_waveform_225_240.json"))
dt, i0 = P["dt"], P["i0"]; pub = np.array(P["amp_x1000"], float) / 1000
sr = 48000
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32)
def env(t0, n):
    out = []
    for k in range(n):
        a = int((t0 + k * dt) * sr); b = int((t0 + (k + 1) * dt) * sr)
        seg = x[a:b]; out.append(seg.max() - seg.min() if len(seg) else 0)
    return np.array(out)
t_pub0 = i0 * dt
best = None
for lag_ms in range(-1500, 1501, 4):
    e = env(t_pub0 + lag_ms / 1000, len(pub))
    c = np.corrcoef(np.log(e + 1e-3), np.log(pub + 1e-3))[0, 1]
    if best is None or c > best[0]:
        best = (c, lag_ms)
corr, lag = best[0], best[1] / 1000
res = {"corr": round(float(corr), 4), "lag_s(260 = published + lag)": lag}
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
def tx(p):
    segs, _ = m.transcribe(p, language="de", vad_filter=False)
    return " ".join(s.text.strip() for s in segs)
tests = []
for a, b in [(233.021, 233.355), (233.021, 233.388), (232.988, 233.355)]:
    a2, b2 = a + lag, b + lag
    f = f"out/nuh_fix/editor_cut_{a:.3f}_{b:.3f}.mp3"
    flt = (f"[0:a]atrim=226:{a2},asetpts=PTS-STARTPTS[x];[0:a]atrim={b2}:236,asetpts=PTS-STARTPTS[y];"
           f"[x][y]concat=n=2:v=0:a=1")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", flt, f], check=True)
    tests.append({"published_cut": [a, b], "in_260": [round(a2, 3), round(b2, 3)], "file": f, "text": tx(f)})
res["tests"] = tests
json.dump(res, open("out/nuh_fix/align.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
