#!/usr/bin/env python3
"""Folge 03 Nuh: test where to cut the wrong word 'nicht' (Koran 11:43 says: 'der mich vor dem Wasser schützt').
Makes the snippet 226-236 s with several cut windows, transcribes each (no prompt), writes report + mp3s."""
import json, os, subprocess, urllib.request
URL = "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge03_nuh_alt_ton_mit_schrittenm4a-K5ddGJhffjV.m4a"
OUT = "out/nuh_fix"; os.makedirs(OUT, exist_ok=True)
src = "/tmp/nuh260.m4a"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
with urllib.request.urlopen(req, timeout=300) as r, open(src, "wb") as f:
    f.write(r.read())
WINDOWS = [(232.95, 233.22), (232.98, 233.24), (232.93, 233.25), (233.00, 233.20)]
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
rep = []
def tx(p):
    segs, _ = m.transcribe(p, language="de", word_timestamps=False, vad_filter=False)
    return " ".join(s.text.strip() for s in segs)
orig = f"{OUT}/orig_226_236.mp3"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "226", "-to", "236", "-i", src, orig], check=True)
rep.append({"cut": None, "file": orig, "text": tx(orig)})
for a, b in WINDOWS:
    f = f"{OUT}/cut_{a:.2f}_{b:.2f}.mp3"
    flt = f"[0:a]atrim=226:{a},asetpts=PTS-STARTPTS,afade=t=out:st={a-226-0.01}:d=0.01[x];[0:a]atrim={b}:236,asetpts=PTS-STARTPTS,afade=t=in:d=0.01[y];[x][y]concat=n=2:v=0:a=1"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", flt, f], check=True)
    rep.append({"cut": [a, b], "file": f, "text": tx(f)})
# loudness envelope 232.6-233.6 in 10 ms steps (to see the gaps between words)
r = subprocess.run(["ffmpeg", "-ss", "232.6", "-to", "233.6", "-i", src, "-af",
                    "astats=metadata=1:reset=1:length=0.01,ametadata=print:key=lavfi.astats.Overall.RMS_level",
                    "-f", "null", "-"], capture_output=True, text=True)
env = [l.split("=")[-1] for l in r.stderr.splitlines() if "RMS_level" in l]
json.dump({"tests": rep, "rms_232.6_233.6_10ms": env}, open(f"{OUT}/report.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=1))
