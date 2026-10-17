#!/usr/bin/env python3
"""Schnittlisten Folgen 15–25: gleiche Regeln wie tools/folgen10_14.py, Daten aus scripts/folgeNN_*.json.
Usage: python3 tools/folgen15_25.py 15 [audio_file_name] """
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import folgen10_14 as m
ROOT = m.ROOT
m.IMG.update(json.load(open(os.path.join(ROOT, "assets", "img_registry_15_25.json"))))
AUDIO = json.load(open(os.path.join(ROOT, "assets", "audio_15_25.json")))
for nr in sys.argv[1:]:
    f = glob.glob(os.path.join(ROOT, "scripts", f"folge{int(nr):02d}_*.json"))[0]
    d = json.load(open(f))
    key = f"folge{d['nr']}_{d['key']}"
    a = AUDIO[key]
    m.EPISODES[key] = {"segments": d["segments"], "plan": d["plan"], "transcript": a["transcript"],
                       "job": a["job"], "audio": a["file"]}
    m.build(key)
