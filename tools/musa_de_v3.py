#!/usr/bin/env python3
"""Musa 14 – German v3: splice the 18 re-recorded lines (branch media-folge14_musa_de_v2,
seg/folge14_musa_de_v2_<key>.mp3) into the published narration, then render, transcribe,
extract check frames, build the SRT and the thumbnail.

Unchanged original pieces (seconds in the published narration, from jobs/dub/folge14_musa.json):
A 0–39.67 (s1a–s1c) · B 107.40–111.07 (s2c) · C 157.30–162.70 (s2f) · D 203.50–207.35 (s3c)
E 257.24–260.27 (s4b) · F 358.40–362.43 (s5c) · G 413.29–416.80 (s6b)
H 445.19–467.68 (s6d+s6e, Noah picture from 462.0) · I 488.86–end (s7a+s7b)
New lines: silence trimmed, 0.25 s before, 0.45 s after, loudness matched to the original.
"""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "render"))
import render  # noqa: E402

SR = 44100
SEG = os.path.join(ROOT, "work", "seg")
OUT = os.path.join(ROOT, "out", "musa_de_v3")
MEDIA = os.path.join(ROOT, "work", "media")     # worktree of branch media-folge14_musa_de_v2
NAME = "folge14_musa_v3"
RAW = "https://raw.githubusercontent.com/belovedofallahkids/boa-render/media-folge14_musa_de_v2/"
PRE, POST = 0.25, 0.45

V2 = json.load(open(os.path.join(ROOT, "jobs", "folge14_musa_v2.json")))
IMG = {s["label"]: s["image"] for s in V2["segments"]}
MOT = {}
for s in V2["segments"]:
    MOT.setdefault(s["script"].split("|")[0], (s["motion"], s["amount"]))

# piece: (kind, key-or-(start,end), [(offset, label, script_key, motion, amount)])
O = lambda a, b: ("orig", (a, b))          # noqa: E731
N = lambda k: ("new", k)                   # noqa: E731
PLAN = [
    (O(0.0, 39.67), [(0.0, "master_A_buch", "s1a", "zoom_in", 0.107), (16.7, "ilyas", "s1b", "zoom_in", 0.05),
                     (21.6, "master_A_buch", "s1c", "pan_left", 0.114)]),
    (N("s2a"), [(0, "pharaoh_palace", "s2a")]),
    (N("s2b"), [(0, "nile_chest", "s2b")]),
    (O(107.40, 111.07), [(0, "noah", "s2c")]),
    (N("s2d"), [(0, "pharaoh_palace", "s2d")]),
    (N("s2e"), [(0, "nile_chest", "s2e")]),
    (O(157.30, 162.70), [(0, "ilyas", "s2f")]),
    (N("s3a"), [(0, "desert_road_long", "s3a")]),
    (N("s3b"), [(0, "madyan_well_sheep", "s3b")]),
    (O(203.50, 207.35), [(0, "noah", "s3c")]),
    (N("s3d"), [(0, "madyan_well_sheep", "s3d")]),
    (N("s4a"), [(0, "mountain_fire", "s4a")]),
    (N("k_s4a"), [(0, "noah", "k_s4a", "zoom_in", 0.05)]),
    (N("s4a_2"), [(0, "holy_valley_light", "s4a_2", "zoom_in", 0.08)]),
    (O(257.24, 260.27), [(0, "ilyas", "s4b")]),
    (N("s4c"), [(0, "staff_glow", "s4c")]),
    (N("s4d"), [(0, "night_dua_sky", "s4d")]),
    (N("s5a"), [(0, "pharaoh_palace", "s5a")]),
    (N("s5b"), [(0, "ropes_courtyard", "s5b")]),
    (O(358.40, 362.43), [(0, "noah", "s5c")]),
    (N("s5d"), [(0, "sunrise_hope", "s5d")]),
    (N("s6a"), [(0, "night_desert_departure", "s6a")]),
    (O(413.29, 416.80), [(0, "ilyas", "s6b")]),
    (N("s6c"), [(0, "sea_split", "s6c")]),
    (O(445.19, 467.68), [(0, "sea_split", "s6d"), (462.0 - 445.19, "noah", "s6e", "zoom_in", 0.05)]),
    (N("s6f"), [(0, "iftar_dates", "s6f")]),
    (O(488.86, None), [(0, "kinder_schlafen", "s7a"), (520.17 - 488.86, "oma_window_night", "s7b")]),
]


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(" ".join(cmd) + "\n" + r.stderr[-2000:])
    return r.stdout + r.stderr


def load(path, af=None):
    cmd = ["ffmpeg", "-hide_banner", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def lufs(x):
    p = os.path.join(ROOT, "work", "_m.wav")
    save(p, x)
    out = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128", "-f", "null", "-"])
    return float(out.rsplit("I:", 1)[1].split("LUFS")[0])


def save(path, x):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", "-c:a", "pcm_s16le", path], input=x.astype(np.float32).tobytes(), check=True)


TRIM = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03,areverse,"
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03,areverse")


def main():
    os.makedirs(OUT, exist_ok=True)
    report = {"pieces": [], "keys": {}}
    orig = load(render.fetch(V2["audio"]))
    L0 = lufs(orig)
    report["orig_lufs"] = L0
    report["orig_len"] = round(len(orig) / SR, 3)
    parts, t, segs = [], 0.0, []
    for (kind, ref), pics in PLAN:
        if kind == "orig":
            a, b = ref
            x = orig[int(round(a * SR)): (len(orig) if b is None else int(round(b * SR)))]
            info = {"piece": f"orig {a}-{b}"}
        else:
            raw = load(os.path.join(SEG, f"folge14_musa_de_v2_{ref}.mp3"))
            y = load(os.path.join(SEG, f"folge14_musa_de_v2_{ref}.mp3"), TRIM)
            li = lufs(y)
            g = 10 ** ((L0 - li) / 20)
            y = y * g
            pk = float(np.max(np.abs(y)))
            if pk > 0.97:
                y *= 0.97 / pk
            x = np.concatenate([np.zeros(int(PRE * SR), np.float32), y, np.zeros(int(POST * SR), np.float32)])
            info = {"piece": ref, "raw_s": round(len(raw) / SR, 3), "trimmed_s": round(len(y) / SR, 3),
                    "lufs_in": li, "gain_db": round(L0 - li, 2), "peak": round(min(pk, 0.97), 3)}
        info["start"] = round(t, 3)
        info["len"] = round(len(x) / SR, 3)
        report["pieces"].append(info)
        for p in pics:
            off, label, key = p[0], p[1], p[2]
            mo, am = (p[3], p[4]) if len(p) > 3 else MOT.get(key, ("zoom_in", 0.08))
            st = round(t + off, 3)
            report["keys"][key] = st
            if segs and segs[-1]["label"] == label:
                segs[-1]["keys"].append(key)       # same picture continues (s6c → s6d)
                continue
            segs.append({"image": IMG[label], "start": st, "motion": mo, "amount": am,
                         "label": label, "script": key, "keys": [key]})
        parts.append(x)
        t += len(x) / SR
    nar = np.concatenate(parts)
    wav = os.path.join(ROOT, "work", "narration.wav")
    save(wav, nar)
    report["narration_len"] = round(len(nar) / SR, 3)

    # persist narration on the media branch (H40)
    mp3 = os.path.join(MEDIA, "full", "folge14_musa_de_v3_narration.mp3")
    os.makedirs(os.path.dirname(mp3), exist_ok=True)
    sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", wav, "-c:a", "libmp3lame", "-b:a", "256k", mp3])
    sh(["git", "-C", MEDIA, "add", "full"])
    sh(["git", "-C", MEDIA, "commit", "-m", "Musa 14 DE v3 narration (spliced) [skip ci]"])
    sh(["git", "-C", MEDIA, "push", "origin", "HEAD:media-folge14_musa_de_v2"])

    for k, s in enumerate(segs):
        s["end"] = segs[k + 1]["start"] if k + 1 < len(segs) else "audio"
        s.pop("keys")
    job = {"name": NAME, "audio": RAW + "full/folge14_musa_de_v3_narration.mp3",
           "crossfade": 0.6, "fade_in": 0.8, "fade_out": 1.0, "tail_hold": 6.0, "loudness": -14,
           "_note": "Musa 14 DE v3 = v2 pictures + 18 re-recorded lines (fixes/folge14_musa_de_v2.json); "
                    "built by tools/musa_de_v3.py",
           "segments": segs}
    jtxt = json.dumps(job, indent=1, ensure_ascii=False)
    jpath = os.path.join(ROOT, "jobs", NAME + ".json")
    open(jpath, "w").write(jtxt)
    json.dump(report, open(os.path.join(OUT, "build.json"), "w"), indent=1, ensure_ascii=False)

    # render (same code as render.yml)
    raw = open(jpath, "rb").read()
    job_hash = hashlib.sha1(raw).hexdigest()
    rdir = os.path.join(ROOT, "out", NAME)
    os.makedirs(rdir, exist_ok=True)
    os.makedirs(render.CACHE, exist_ok=True)
    status = render.render_job(json.loads(raw), job_hash, rdir)
    json.dump(status, open(os.path.join(rdir, "status.json"), "w"), indent=2, ensure_ascii=False)
    open(os.path.join(rdir, "log.txt"), "w").write("\n".join(render.LOG[-300:]))
    print(json.dumps(status, indent=1))


if __name__ == "__main__":
    main()
