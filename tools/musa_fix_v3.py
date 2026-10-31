#!/usr/bin/env python3
"""Musa 14 – German v3 (31.10.2026): new narration = unchanged original pieces + 18 re-recorded
lines (fixes/folge14_musa_de_v2.json, owner-approved), then a new render job jobs/folge14_musa_v3.json.
Runs on GitHub Actions (orshot audio is reachable there). Inputs: seg/folge14_musa_de_v2_<key>.mp3
(from branch media-folge14_musa_de_v2). Output: work/musa_v3/folge14_musa_de_v3.mp3 + plan json."""
import json, os, subprocess, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(ROOT, "work", "musa_v3")
os.makedirs(W, exist_ok=True)
V2 = json.load(open(os.path.join(ROOT, "jobs", "folge14_musa_v2.json")))
IMG, EXTRA = {}, {}
for s in V2["segments"]:
    IMG.setdefault(s["image"].split("/")[-1].split("-")[0], s["image"])
    EXTRA.setdefault(s["image"], {k: s[k] for k in ("motion", "amount", "crop") if k in s})
def img(prefix):
    for k, v in IMG.items():
        if k.startswith(prefix):
            return v
    raise KeyError(prefix)

# piece: ("orig", start, end, [(rel_time, image_prefix), ...]) or ("new", key, image_prefix)
PLAN = [
    ("orig", 0.0, 39.67, [(0, "boa_master_A_buch"), (16.7, "boa_ilyas_allein"), (21.6, "boa_master_A_buch")]),
    ("new", "s2a", "boa_folge14_pharaoh_palace"),
    ("new", "s2b", "boa_folge14_nile_chest"),
    ("orig", 107.40, 111.07, [(0, "boa_noah_allein")]),
    ("new", "s2d", "boa_folge14_pharaoh_palace"),
    ("new", "s2e", "boa_folge14_nile_chest"),
    ("orig", 157.30, 162.70, [(0, "boa_ilyas_allein")]),
    ("new", "s3a", "boa_folge14_desert_road"),
    ("new", "s3b", "boa_folge14_madyan_well"),
    ("orig", 203.50, 207.35, [(0, "boa_noah_allein")]),
    ("new", "s3d", "boa_folge14_madyan_well"),
    ("new", "s4a", "boa_folge14_mountain_fire"),
    ("new", "k_s4a", "boa_noah_allein"),
    ("new", "s4a_2", "boa_folge14_holy_valley"),
    ("orig", 257.24, 260.27, [(0, "boa_ilyas_allein")]),
    ("new", "s4c", "boa_folge14_staff_glow"),
    ("new", "s4d", "boa_folge12_night_dua"),
    ("new", "s5a", "boa_folge14_pharaoh_palace"),
    ("new", "s5b", "boa_folge14_ropes_courtyard"),
    ("orig", 358.40, 362.43, [(0, "boa_noah_allein")]),
    ("new", "s5d", "boa_folge09_sunrise_hope"),
    ("new", "s6a", "boa_folge14_night_desert_departure"),
    ("orig", 413.29, 416.80, [(0, "boa_ilyas_allein")]),
    ("new", "s6c", "boa_folge15_sea_split"),
    ("orig", 445.19, 467.68, [(0, "boa_folge15_sea_split"), (462.0 - 445.19, "boa_noah_allein")]),
    ("new", "s6f", "boa_folge14_iftar_dates"),
    ("orig", 488.86, None, [(0, "boa_kinder_schlafen"), (520.17 - 488.86, "boa_oma_window_night")]),
]

def sh(*a):
    subprocess.run(a, check=True)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

src = os.path.join(W, "orig.mp3")
if not os.path.exists(src):
    req = urllib.request.Request(V2["audio"], headers={"User-Agent": "Mozilla/5.0"})
    open(src, "wb").write(urllib.request.urlopen(req, timeout=180).read())
total_src = dur(src)
FMT = ["-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le"]
parts, segs, report, t = [], [], [], 0.0
for i, p in enumerate(PLAN):
    out = os.path.join(W, f"p{i:02d}.wav")
    if p[0] == "orig":
        a, b = p[1], (p[2] if p[2] is not None else total_src)
        sh("ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-to", f"{b}", "-i", src,
           "-af", "afade=t=in:d=0.015,areverse,afade=t=in:d=0.015,areverse", *FMT, out)
        imgs = p[3]
        label = f"orig {a}-{b:.2f}"
    else:
        f = os.path.join(ROOT, "seg", f"folge14_musa_de_v2_{p[1]}.mp3")
        sh("ffmpeg", "-v", "error", "-y", "-i", f, "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
           "adelay=250|250,apad=pad_dur=0.45", *FMT, out)
        imgs = [(0, p[2])]
        label = f"new {p[1]}"
    d = dur(out)
    for k, (rel, pref) in enumerate(imgs):
        end = t + (imgs[k + 1][0] if k + 1 < len(imgs) else d)
        if segs and segs[-1]["image"] == img(pref):
            segs[-1]["end"] = round(end, 3)  # same picture continues
        else:
            segs.append({"image": img(pref), "start": round(t + rel, 3), "end": round(end, 3), **EXTRA[img(pref)]})
    report.append({"piece": label, "start": round(t, 3), "dur": round(d, 3)})
    parts.append(out)
    t += d
segs[-1]["end"] = "audio"
lst = os.path.join(W, "list.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
wav = os.path.join(W, "full.wav")
sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, *FMT, wav)
mp3 = os.path.join(W, "folge14_musa_de_v3.mp3")
sh("ffmpeg", "-v", "error", "-y", "-i", wav, "-ar", "44100", "-ac", "2", "-b:a", "192k", mp3)
job = {k: v for k, v in V2.items() if k != "segments"}
job["name"] = "folge14_musa_v3"
job["audio"] = os.environ["AUDIO_URL"]
job["segments"] = segs
json.dump(job, open(os.path.join(ROOT, "jobs", "folge14_musa_v3.json"), "w"), indent=1, ensure_ascii=False)
os.makedirs(os.path.join(ROOT, "out", "folge14_musa_v3"), exist_ok=True)
json.dump({"pieces": report, "audio_len": round(t, 3), "segments": len(segs)},
          open(os.path.join(ROOT, "out", "folge14_musa_v3", "plan_report.json"), "w"), indent=1)
print("audio", round(t, 2), "s,", len(segs), "picture segments")
