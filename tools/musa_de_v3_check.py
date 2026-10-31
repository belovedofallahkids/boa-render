#!/usr/bin/env python3
"""Checks on the FINAL Musa v3 files (H35): word transcript vs approved text per key,
silence/black detection, one full-res frame per picture segment, chapters, German SRT,
series thumbnail (layout of Orshot template 26008)."""
import difflib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "render"))
import render  # noqa: E402

NAME = "folge14_musa_v3"
OUT = os.path.join(ROOT, "out", "musa_de_v3")
MEDIA = os.path.join(ROOT, "work", "media")
WAV = os.path.join(ROOT, "work", "narration.wav")
VIDEO = os.path.join(ROOT, "work", NAME, NAME + ".mp4")
ORDER = ["s1a", "s1b", "s1c", "s2a", "s2b", "s2c", "s2d", "s2e", "s2f", "s3a", "s3b", "s3c", "s3d", "s4a",
         "k_s4a", "s4a_2", "s4b", "s4c", "s4d", "s5a", "s5b", "s5c", "s5d", "s6a", "s6b", "s6c", "s6d", "s6e",
         "s6f", "s7a", "s7b"]
CHAPTERS = [("s1a", "Ein Baby im Fluss?"), ("s2a", "Die Kiste auf dem Fluss"), ("s3a", "In Madyan"),
            ("s4a", "Das Feuer am Berg"), ("s5a", "Bei Pharao"), ("s6a", "Das Meer"),
            ("s7a", "Die Lehre & Gute Nacht")]


def norm(w):
    return re.sub(r"[^a-zäöüß0-9]", "", w.lower())


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stderr


def mmss(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def main():
    build = json.load(open(os.path.join(OUT, "build.json")))
    keys = build["keys"]
    old = {s["id"]: s["de"] for s in json.load(open(os.path.join(ROOT, "jobs", "dub", "folge14_musa.json")))["segments"]}
    new = {k: v["de"] for k, v in json.load(open(os.path.join(ROOT, "fixes", "folge14_musa_de_v2.json")))["segments"].items()}
    text = {k: new.get(k, old.get(k)) for k in ORDER}
    script = {"name": NAME, "segments": text}
    os.makedirs(os.path.join(ROOT, "scripts"), exist_ok=True)
    json.dump(script, open(os.path.join(ROOT, "scripts", NAME + ".json"), "w"), indent=1, ensure_ascii=False)

    # 1) word transcript of the final narration
    from faster_whisper import WhisperModel
    m = WhisperModel("medium", device="cpu", compute_type="int8")
    segs, info = m.transcribe(WAV, language="de", word_timestamps=True, beam_size=5, vad_filter=False)
    tr = {"name": NAME, "model": "medium", "duration": info.duration, "segments": []}
    for s in segs:
        tr["segments"].append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                               "words": [{"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word.strip()}
                                         for w in (s.words or [])]})
    tpath = os.path.join(ROOT, "out", "transcripts", NAME + "_ton.json")
    os.makedirs(os.path.dirname(tpath), exist_ok=True)
    json.dump(tr, open(tpath, "w"), indent=0, ensure_ascii=False)
    words = [w for s in tr["segments"] for w in s["words"]]

    # 2) per key: heard words vs approved text
    bounds = [(k, keys[k]) for k in ORDER]
    rep = []
    for i, (k, st) in enumerate(bounds):
        en = bounds[i + 1][1] if i + 1 < len(bounds) else 1e9
        heard = [w["word"] for w in words if st - 0.15 <= (w["start"] + w["end"]) / 2 < en - 0.15]
        exp = re.sub(r"\[[^\]]*\]", " ", text[k]).split()
        a, b = [norm(x) for x in exp if norm(x)], [norm(x) for x in heard if norm(x)]
        sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
        diffs = [{"op": op, "expected": " ".join(a[i1:i2]), "heard": " ".join(b[j1:j2])}
                 for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
        rep.append({"key": k, "start": st, "new": k in new, "ratio": round(sm.ratio(), 3),
                    "heard": " ".join(heard), "diffs": diffs})
    json.dump(rep, open(os.path.join(OUT, "text_check.json"), "w"), indent=1, ensure_ascii=False)

    # 3) technique on the final video
    sil = run(["ffmpeg", "-hide_banner", "-nostats", "-i", VIDEO, "-af", "silencedetect=n=-45dB:d=2.5", "-f", "null", "-"])
    blk = run(["ffmpeg", "-hide_banner", "-nostats", "-i", VIDEO, "-vf", "blackdetect=d=0.3:pix_th=0.08", "-an", "-f", "null", "-"])
    tech = {"silence_over_2_5s": [l.split("] ")[-1] for l in sil.splitlines() if "silence_" in l],
            "black": [l.split("] ")[-1] for l in blk.splitlines() if "black_start" in l],
            "loudness": render.check_loudness(VIDEO), "video_s": render.duration(VIDEO), "narration_s": render.duration(WAV)}
    json.dump(tech, open(os.path.join(OUT, "tech.json"), "w"), indent=1)

    # 4) one full-res frame per picture segment (middle) → media branch, small copy → main
    job = json.load(open(os.path.join(ROOT, "jobs", NAME + ".json")))
    fdir = os.path.join(MEDIA, "frames_v3")
    sdir = os.path.join(OUT, "frames")
    os.makedirs(fdir, exist_ok=True)
    os.makedirs(sdir, exist_ok=True)
    segl = job["segments"]
    for n, s in enumerate(segl):
        end = s["end"] if s["end"] != "audio" else tech["video_s"] - 1.0
        t = (s["start"] + end) / 2
        base = f"{n:02d}_{s['label']}_{t:06.1f}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", VIDEO, "-frames:v", "1", "-q:v", "3",
                        os.path.join(fdir, base)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(fdir, base), "-vf", "scale=640:-1",
                        "-q:v", "5", os.path.join(sdir, base)], check=True)

    # 5) chapters + SRT
    chap = "\n".join(f"{mmss(keys[k]) if k != 's1a' else '0:00'} {t}" for k, t in CHAPTERS)
    open(os.path.join(OUT, "chapters.txt"), "w").write(chap + "\n")
    os.makedirs(os.path.join(ROOT, "subs"), exist_ok=True)
    print(subprocess.run([sys.executable, os.path.join(ROOT, "tools", "subs.py"), os.path.join(ROOT, "scripts", NAME + ".json"),
                          tpath, os.path.join(ROOT, "subs", NAME + "_de.srt")], capture_output=True, text=True).stdout)

    # 6) thumbnail (series layout 26008): master_A_buch left (from the 26008 render), sea_split right
    scene = render.fetch(job["segments"][[s["label"] for s in segl].index("sea_split")]["image"])
    th = os.path.join(ROOT, "assets", "thumbnails", "boa_folge14_thumbnail_serie_v2.jpg")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "thumb_serie.py"),
                    os.path.join(ROOT, "assets", "thumbnails", "boa_folge14_thumbnail_serie.jpg"),
                    scene, "Das Meer teilt sich", "MUSA", th], check=True, cwd=ROOT)
    render.publish(NAME, [th, os.path.join(ROOT, "subs", NAME + "_de.srt")])

    subprocess.run(["git", "-C", MEDIA, "add", "frames_v3"], check=True)
    subprocess.run(["git", "-C", MEDIA, "commit", "-m", "Musa v3 check frames [skip ci]"], check=True)
    subprocess.run(["git", "-C", MEDIA, "push", "origin", "HEAD:media-folge14_musa_de_v2"], check=True)
    bad = [r for r in rep if r["ratio"] < 0.97]
    print("keys below 0.97:", [(r["key"], r["ratio"]) for r in bad])
    print(json.dumps(tech, indent=1))


if __name__ == "__main__":
    main()
