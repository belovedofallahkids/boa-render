#!/usr/bin/env python3
"""Dub job for one finished episode: German segment times from the word transcript.
Usage: python3 tools/dub_job.py 15 ar,en"""
import glob, json, os, re, sys, difflib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nr, langs = int(sys.argv[1]), sys.argv[2].split(",")
sf = glob.glob(os.path.join(ROOT, "scripts", f"folge{nr:02d}_*.json"))[0]
d = json.load(open(sf)); key = f"folge{d['nr']}_{d['key']}"
audio = json.load(open(os.path.join(ROOT, "assets", "audio_15_25.json")))[key]
tr = json.load(open(os.path.join(ROOT, "out", "transcripts", audio["transcript"] + ".json")))
norm = lambda w: re.sub(r"[^a-zäöüß0-9]", "", w.lower())
tw = [(w["start"], w["end"], norm(w["word"])) for s in tr["segments"] for w in s["words"] if norm(w["word"])]
nums = {"vierzig": "40"}
sw, own = [], []
for sid, t in d["segments"].items():
    for tok in re.sub(r"\[[^\]]*\]", " ", t).split():
        w = nums.get(norm(tok), norm(tok))
        if w:
            sw.append(w); own.append(sid)
sm = difflib.SequenceMatcher(a=sw, b=[x[2] for x in tw], autojunk=False)
m = {}
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        m[a + k] = b + k
segs = []
for sid in d["segments"]:
    idx = [i for i, o in enumerate(own) if o == sid and i in m]
    segs.append({"id": sid, "start": tw[m[idx[0]]][0], "end": tw[m[idx[-1]]][1], "kid": sid in d["kids"],
                 "de": d["segments"][sid]})
job = {"name": f"{key}_dub", "episode": key, "duration": tr["duration"], "langs": langs, "prophet": d["prophet"],
       "ref_audio": "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge14_erzaehlung_komplett_2026-10-16mp3-hxXoUqUsSzs.mp3",
       "ref": [45.0, 56.5], "kid_ref": [203.5, 207.0], "segments": segs}
json.dump(job, open(os.path.join(ROOT, "jobs", "dub", f"{key}.json"), "w"), indent=1, ensure_ascii=False)
print(key, len(segs), "segments, duration", tr["duration"])
