#!/usr/bin/env python3
"""Dub jobs for episodes 10-14 (scripts in tools/folgen10_14_skripte.json, timing from the word transcript).
Usage: python3 tools/dub_job_10_14.py ar,tr,fr [10,11,...]"""
import difflib, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
langs = sys.argv[1].split(",")
D = json.load(open(os.path.join(ROOT, "tools", "folgen10_14_skripte.json")))
eps = sys.argv[2].split(",") if len(sys.argv) > 2 else list(D)
PROPHET = {"10": "Yaqub", "11": "Yusuf", "12": "Ayyub", "13": "Shuaib", "14": "Musa"}
REF = "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge14_erzaehlung_komplett_2026-10-16mp3-hxXoUqUsSzs.mp3"
norm = lambda w: re.sub(r"[^a-zäöüß0-9]", "", w.lower())
for nr in eps:
    d = D[nr]
    key = d["job"].rsplit("_v", 1)[0]
    tr = json.load(open(os.path.join(ROOT, "out", "transcripts", d["transcript"] + ".json")))
    tw = [(w["start"], w["end"], norm(w["word"])) for s in tr["segments"] for w in s["words"] if norm(w["word"])]
    sw, own = [], []
    for sid, t in d["segments"].items():
        for tok in re.sub(r"\[[^\]]*\]", " ", t).split():
            if norm(tok):
                sw.append(norm(tok)); own.append(sid)
    sm = difflib.SequenceMatcher(a=sw, b=[x[2] for x in tw], autojunk=False)
    m = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            m[a + k] = b + k
    segs, bad = [], []
    for sid, t in d["segments"].items():
        idx = [i for i, o in enumerate(own) if o == sid and i in m]
        if not idx:
            bad.append(sid); continue
        segs.append({"id": sid, "start": tw[m[idx[0]]][0], "end": tw[m[idx[-1]]][1],
                     "kid": "childlike" in t, "de": t})
    if bad:
        print(key, "NOT MATCHED", bad); continue
    job = {"name": f"{key}_dub", "episode": key, "duration": tr["duration"], "langs": langs, "prophet": PROPHET[nr],
           "ref_audio": REF, "ref": [45.0, 56.5], "kid_ref": [203.5, 207.0], "segments": segs}
    json.dump(job, open(os.path.join(ROOT, "jobs", "dub", f"{key}.json"), "w"), indent=1, ensure_ascii=False)
    print(key, len(segs), "segments", tr["duration"])
