#!/usr/bin/env python3
"""Plan C: remove the whole damaged clause 'der schützt ... dem Wasser' between two silences.
Editor (current version) 3:51:22 - 3:54:19  ==  260 audio 231.764 - 235.000 (after the first cut, mapping +0.031 s)."""
import json, subprocess, urllib.request
URL = "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge03_nuh_alt_ton_mit_schrittenm4a-K5ddGJhffjV.m4a"
src = "/tmp/nuh260.m4a"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
with urllib.request.urlopen(req, timeout=300) as r, open(src, "wb") as f:
    f.write(r.read())
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
out = {}
for name, (a, b) in {"plan_c": (231.764, 235.000), "plan_c_early": (231.60, 234.70), "plan_c_late": (231.95, 235.30)}.items():
    f = f"out/nuh_fix/{name}_222_245.mp3"
    flt = f"[0:a]atrim=222:{a},asetpts=PTS-STARTPTS[x];[0:a]atrim={b}:245,asetpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=0:a=1"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", flt, f], check=True)
    segs, _ = m.transcribe(f, language="de", vad_filter=False)
    out[name] = {"cut_260": [a, b], "text": " ".join(s.text.strip() for s in segs)}
    r = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=1.2", "-f", "null", "-"], capture_output=True, text=True)
    out[name]["silences"] = [l.split("] ")[1] for l in r.stderr.splitlines() if "silence_" in l]
json.dump(out, open("out/nuh_fix/plan_c.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
