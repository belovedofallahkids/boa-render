#!/usr/bin/env python3
"""Free check of a PUBLISHED video's sound: download audio (yt-dlp), word transcript
without prompt (no bias), save to out/transcripts/<name>.txt. Usage: yt_check.py <videoId> <name>"""
import json, os, subprocess, sys
vid, name = sys.argv[1], sys.argv[2]
out = os.path.join("out", "transcripts"); os.makedirs(out, exist_ok=True)
src = f"/tmp/{name}.m4a"
r = subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", src, f"https://www.youtube.com/watch?v={vid}"],
                   capture_output=True, text=True)
open(os.path.join(out, name + ".ytdlp.log"), "w").write(r.stdout[-3000:] + r.stderr[-3000:])
if r.returncode != 0:
    sys.exit(0)
dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                     capture_output=True, text=True).stdout.strip()
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
segs, _ = m.transcribe(src, language="de", word_timestamps=True, vad_filter=False)
lines, res = [], []
for s in segs:
    ws = [{"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word.strip()} for w in (s.words or [])]
    res.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": ws})
    lines += [f"{w['start']:8.3f} {w['end']:8.3f} {w['word']}" for w in ws]
json.dump({"video": vid, "duration": dur, "segments": res}, open(os.path.join(out, name + ".json"), "w"), ensure_ascii=False, indent=1)
open(os.path.join(out, name + ".txt"), "w").write("\n".join(lines) + "\n")
print("ok", dur, len(lines))
