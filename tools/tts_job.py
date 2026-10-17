#!/usr/bin/env python3
"""Make a free Chatterbox voice job (Oma voice cloned from Folge 14) for one script.
Usage: python3 tools/tts_job.py scripts/folge16_dhulkifl.json"""
import json, sys
d = json.load(open(sys.argv[1]))
lines, prev = [], None
for k, t in d["segments"].items():
    gap = 0 if prev is None else (0.6 if k[1] == prev else 1.2)
    prev = k[1]
    lines.append({"id": k, "text": t, "kid": k in d["kids"], "gap_before": gap})
name = f"folge{d['nr']}_{d['key']}_cb"
job = {"name": name, "engines": ["chatterbox"],
       "ref_audio": "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge14_erzaehlung_komplett_2026-10-16mp3-hxXoUqUsSzs.mp3",
       "ref": [45.0, 56.5], "kid_ref": [203.5, 207.0], "cfg": 0.3, "lines": lines}
json.dump(job, open(f"jobs/tts/{name}.json", "w"), indent=1, ensure_ascii=False)
print(name, len(lines))
