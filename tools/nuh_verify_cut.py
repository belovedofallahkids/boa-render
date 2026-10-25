#!/usr/bin/env python3
"""After the YouTube Editor cut: find which part of Orshot audio 260 was removed, by matching the new
published waveform (Studio editor data) against 260 with a modelled cut. Then rebuild + transcribe."""
import json, subprocess, urllib.request
import numpy as np
URL = "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge03_nuh_alt_ton_mit_schrittenm4a-K5ddGJhffjV.m4a"
src = "/tmp/nuh260.m4a"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
with urllib.request.urlopen(req, timeout=300) as r, open(src, "wb") as f:
    f.write(r.read())
sr = 48000
x = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout, np.float32)
N = json.load(open("out/nuh_fix/published_waveform_after_cut_225_240.json"))
dt, i0 = N["dt"], N["i0"]; new = np.array(N["amp_x1000"], float) / 1000
tn = (i0 + np.arange(len(new))) * dt          # waveform time of each new sample
def amp(y, t):                                 # max-min of y in [t, t+dt)
    a = int(t * sr); b = int((t + dt) * sr); s = y[a:b]
    return s.max() - s.min() if len(s) else 0.0
sel = (tn > 231.0) & (tn < 236.5)
L = lambda v: np.log(v + 1e-3)
best = None
for lag in np.arange(-0.20, 0.0001, 0.004):           # 260 time = waveform time + lag (before the cut)
    for c0 in np.arange(232.80, 233.30, 0.004):        # cut start in 260 time
        for ln in (0.334,):
            y = np.concatenate([x[:int(c0 * sr)], x[int((c0 + ln) * sr):]])
            e = np.array([amp(y, t + lag) for t in tn[sel]])
            c = np.corrcoef(L(e), L(new[sel]))[0, 1]
            if best is None or c > best[0]:
                best = (c, lag, c0, ln)
c, lag, c0, ln = best
res = {"corr": round(float(c), 4), "lag": round(float(lag), 3), "removed_in_260": [round(float(c0), 3), round(float(c0 + ln), 3)]}
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
f = "out/nuh_fix/after_cut_rebuilt_226_236.mp3"
flt = f"[0:a]atrim=226:{c0},asetpts=PTS-STARTPTS[a];[0:a]atrim={c0+ln}:236,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", flt, f], check=True)
segs, _ = m.transcribe(f, language="de", word_timestamps=True, vad_filter=False)
res["text"] = " ".join(s.text.strip() for s in segs)
w260 = [l.split() for l in open("out/transcripts/folge03_nuh_alt_260_ohneprompt.txt") if l.strip()]
res["words_260_touched"] = [w for w in w260 if float(w[1]) > c0 - 0.05 and float(w[0]) < c0 + ln + 0.05]
json.dump(res, open("out/nuh_fix/verify_after_cut.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
