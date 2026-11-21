#!/usr/bin/env python3
"""Episode build (Folge 17+): ElevenLabs Oma takes -> narration + transcript -> cut list -> render.
Same rules as dk16_build.py (narration) and folgen10_14.py (cuts: H9 kids only on own line, H12 sleeping
kids only from «sie schlafen schon», no picture twice in a row). Every shot moves (2.5D camera, H59 minimum).
Usage: EP=17 python3 tools/ep_build.py narration|cuts
Inputs: scripts/folgeNN_*.json (segments, kids, plan), release <ep>_el_src (one mp3 per segment),
        prompts/h59_<ep>.json (approved pictures; their files override old registry pictures of the same name),
        optional "plan_v2" in the script (used instead of "plan")."""
import glob, json, os, subprocess, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
NR = int(os.environ["EP"])
SF = glob.glob(os.path.join(ROOT, "scripts", f"folge{NR:02d}_*.json"))[0]
S = json.load(open(SF))
KEY = f"folge{S['nr']}_{S['key']}"
REL = f"https://github.com/belovedofallahkids/boa-render/releases/download/{KEY}_el_src/"
W = os.path.join(ROOT, "work_ep"); os.makedirs(W, exist_ok=True)
RAW = "https://raw.githubusercontent.com/belovedofallahkids/boa-render/main/"
def sh(*c): subprocess.run(c, check=True)


def narration():
    order = list(S["segments"])
    parts = []
    for i, k in enumerate(order):
        f = f"{W}/{k}.mp3"; urllib.request.urlretrieve(f"{REL}{KEY}_{k}.mp3", f)
        t = f"{W}/{k}.wav"
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", f, "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse",
           "-ar", "44100", "-ac", "1", t)
        parts.append(t)
        if i + 1 < len(order):
            nxt = order[i + 1]
            gap = 1.1 if nxt[:2] != k[:2] else (0.6 if (k in S["kids"] or nxt in S["kids"]) else 0.8)
            g = f"{W}/gap_{k}.wav"
            sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(gap), g)
            parts.append(g)
    lst = f"{W}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    out = f"{W}/{KEY}_de.mp3"
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-af",
       "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", out)
    from faster_whisper import WhisperModel
    m = WhisperModel("medium", device="cpu", compute_type="int8")
    names = ", ".join(sorted({S["prophet"], S.get("prev", ""), S.get("next", "")} - {""}))
    segs, _ = m.transcribe(out, language="de", word_timestamps=True,
                           initial_prompt=f"Oma erzählt Noah und Ilyas vom Propheten {S['prophet']}. {names}, Talut, Jalut, Zabur, Subhanallah.")
    td = os.path.join(ROOT, "out", "transcripts"); os.makedirs(td, exist_ok=True)
    rows, txt = [], []
    for s in segs:
        txt.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        for w in s.words:
            rows.append(f"{w.start:.3f} {w.end:.3f} {w.word.strip()}")
    open(os.path.join(td, f"{KEY}_ton.txt"), "w").write("\n".join(rows) + "\n")
    json.dump({"segments": txt}, open(os.path.join(td, f"{KEY}_ton.json"), "w"), ensure_ascii=False, indent=1)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                         capture_output=True, text=True).stdout.strip()
    print("duration", dur)


def cuts():
    import folgen10_14 as m
    reg = json.load(open(os.path.join(ROOT, "assets", "img_registry_15_25.json")))
    full = {k: m.B + v for k, v in {**m.IMG, **reg}.items()}
    p = os.path.join(ROOT, "prompts", f"h59_{KEY}.json")
    if os.path.exists(p):  # approved free pictures win over older pictures with the same scene name
        for im in json.load(open(p))["images"]:
            if im.get("status") == "approved" and im.get("file"):
                full[im.get("scene") or im["id"]] = RAW + im["file"]
    m.B = ""
    m.IMG.clear(); m.IMG.update(full)
    plan = S.get("plan_v2") or S["plan"]
    missing = sorted({x[1] for x in plan} - set(full))
    if missing:
        raise SystemExit(f"pictures missing: {missing}")
    job = f"{KEY}_v1"
    m.EPISODES[KEY] = {"segments": S["segments"], "plan": plan, "transcript": f"{KEY}_ton", "job": job,
                       "audio": f"https://github.com/belovedofallahkids/boa-render/releases/download/{KEY}_audio/{KEY}_de.mp3"}
    m.build(KEY)


if __name__ == "__main__":
    {"narration": narration, "cuts": cuts}[sys.argv[1]]()
