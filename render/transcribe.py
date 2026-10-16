#!/usr/bin/env python3
"""Word-level transcripts on GitHub Actions (free), for exact cut points.

jobs/transcribe/<name>.json: {"name": "...", "audio": "https://...", "language": "de", "model": "small"}
-> out/transcripts/<name>.json  (segments with words: start, end, word)
-> out/transcripts/<name>.txt   (one line per word: start end word)
"""
import glob
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "transcripts")


def pending():
    todo = []
    for jf in sorted(glob.glob(os.path.join(ROOT, "jobs", "transcribe", "*.json"))):
        raw = open(jf, "rb").read()
        job = json.loads(raw)
        h = hashlib.sha1(raw).hexdigest()
        st = os.path.join(OUT, job["name"] + ".json")
        if os.path.exists(st) and json.load(open(st)).get("job_hash") == h:
            continue
        todo.append((job, h))
    return todo


def main():
    todo = pending()
    if not todo:
        print("no transcribe jobs")
        return
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper==1.1.1"], check=True)
    from faster_whisper import WhisperModel  # noqa: E402

    os.makedirs(OUT, exist_ok=True)
    models = {}
    for job, h in todo:
        name = job["name"]
        src = os.path.join(OUT, name + ".audio")
        req = urllib.request.Request(job["audio"], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
        with urllib.request.urlopen(req, timeout=300) as r, open(src, "wb") as f:
            f.write(r.read())
        size = job.get("model", "small")
        if size not in models:
            models[size] = WhisperModel(size, device="cpu", compute_type="int8")
        segs, info = models[size].transcribe(src, language=job.get("language", "de"),
                                             word_timestamps=True, vad_filter=False,
                                             initial_prompt=job.get("prompt"))
        result, lines = [], []
        for s in segs:
            words = [{"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word.strip()}
                     for w in (s.words or [])]
            result.append({"start": round(s.start, 3), "end": round(s.end, 3),
                           "text": s.text.strip(), "words": words})
            lines += [f"{w['start']:8.3f} {w['end']:8.3f} {w['word']}" for w in words]
        json.dump({"name": name, "job_hash": h, "duration": round(info.duration, 3),
                   "model": size, "segments": result},
                  open(os.path.join(OUT, name + ".json"), "w"), indent=1, ensure_ascii=False)
        open(os.path.join(OUT, name + ".txt"), "w").write("\n".join(lines) + "\n")
        os.remove(src)
        print("transcribed", name, len(lines), "words")


if __name__ == "__main__":
    main()
