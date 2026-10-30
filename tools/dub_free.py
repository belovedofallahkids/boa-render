#!/usr/bin/env python3
"""Free dub track per language (owner 30.10.2026: «مجانا», H54).

Text: dub/<ep>_<lang>_from_ar_v1.json (translated from the Arabic mother text, H44-a).
Voice: edge-tts (Microsoft neural, free), one warm female voice per language, slower.
Children's lines (Noah/Ilyas images): same voice, slightly higher pitch.
Placement like the approved Arabic track (H46/H49): every line starts with its image (+0.35 s);
extra lines x_<key> follow their sentence; open before s1a; s7b -> close -> final without a pause
gap before the closing; all remaining silence at the very end.
Checks (H35/H46): overrun of the next image, gaps > 1.2 s, LUFS, whisper transcript vs text per line.
Output: release dub_<ep>_free: <ep>_<lang>_free_{VER}.mp3 + <ep>_<lang>_free_{VER}_report.json
DRAFT – owner listens before any upload (H46.6); bs/sq need a human reviewer (H44.6).
"""
import asyncio, difflib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "belovedofallahkids/boa-render")
EP = os.environ.get("DUB_EP", "folge10_yaqub")
LANG = os.environ["DUB_LANG"]
TAG = f"dub_{EP}_free"
VOICE = {
    "fr": ("fr-FR-VivienneMultilingualNeural", "-10%", "-2Hz"),
    "en": ("en-US-AvaMultilingualNeural", "-10%", "-2Hz"),
    "tr": ("tr-TR-EmelNeural", "-10%", "-3Hz"),
    "bs": ("bs-BA-VesnaNeural", "-15%", "-4Hz"),
    "sq": ("sq-AL-AnilaNeural", "-15%", "-4Hz"),
}
KID_PITCH = "+22Hz"
OD = f"/tmp/dubfree_{LANG}"
VER = "v2" if os.environ.get("DUB_FILL") == "1" else "v1"


def sh(*a, **k):
    return subprocess.run(list(a), check=True, **k)


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]))


def clean(t):
    t = re.sub(r"\[[^\]]*\]", "", str(t)).replace("…", "... ")
    return re.sub(r"\s+", " ", t).strip()


async def tts(text, voice, rate, pitch, out):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out)


def main():
    os.makedirs(OD, exist_ok=True)
    tx = json.load(open(f"{ROOT}/dub/{EP}_{LANG}_from_ar_v1.json", encoding="utf-8"))
    import glob
    jf = os.environ.get("DUB_JOB") or sorted(glob.glob(f"{ROOT}/jobs/{EP}_v*.json"),
                                              key=lambda x: int(re.findall(r"_v(\d+)\.json$", x)[0]))[-1]
    job = json.load(open(jf))
    segs = job["segments"]
    T = float(os.environ.get("DUB_DURATION") or (463.8 if EP == "folge10_yaqub" else
              (job["segments"][-1]["end"] if job["segments"][-1].get("end") not in (None, "audio") else 0)))
    if not T and job.get("audio", "").startswith("http"):
        try:  # video length = narration audio + tail_hold (how the render was built)
            T = round(dur(job["audio"]) + float(job.get("tail_hold") or 0), 1)
            print("video length from job audio:", T, flush=True)
        except Exception as ex:
            print("audio length failed:", ex, flush=True)
    if not T:
        T = max(s["start"] for s in segs) + 40.0  # fallback; real length is set from the published video
    img = {}
    for s in segs:
        img.setdefault(s["script"], s)
    starts = sorted(s["start"] for s in segs)
    kids = {s["script"] for s in segs if s["label"] in ("noah", "ilyas")}
    # split lines (owner choice «ب» 30.10.2026): "<key>_2" starts on the 2nd image of that sentence
    # (job script "<key>|…"); "k_<key>" = short kid question between the parts (kid voice, no new info, H55)
    for s in segs:
        base = str(s["script"]).split("|")[0]
        if "|" in str(s["script"]) and base + "_2" not in img:
            img[base + "_2"] = s
    keys = [k for k in tx if not k.startswith("_")]
    # gap lines (owner choice «أ» 30.10.): only with DUB_FILL=1, i.e. after owner approval of the Arabic text
    fp = f"{ROOT}/dub/{EP}_fill_v1.json"
    if os.environ.get("DUB_FILL") == "1" and os.path.exists(fp):
        fill = json.load(open(fp, encoding="utf-8"))
        for fk, fv in fill.items():
            if fk.startswith("_") or LANG not in fv or fv["after"] not in keys:
                continue
            tx[fk] = fv[LANG]
            keys.insert(keys.index(fv["after"]) + 1, fk)
    voice, rate, pitch = VOICE[LANG]

    # 1) TTS every line (one call each, free)
    clips = {}
    for k in keys:
        out = f"{OD}/{k}.mp3"
        asyncio.run(tts(clean(tx[k]), voice, rate, KID_PITCH if (k in kids or k.startswith("k_")) else pitch, out))
        clips[k] = out
        print("tts", k, round(dur(out), 1), flush=True)

    # 1b) opening fix (owner 30.10.: «صلح جملة البداية»): open + s1a share the first image and must end
    # before Ilyas's image (s1b). If too long, re-voice both at one faster rate (natural TTS, not atempo).
    if "open" in clips and "s1a" in clips and "s1b" in img:
        room = img["s1b"]["start"] - 0.3 - 0.55 - 0.25
        need = dur(clips["open"]) + dur(clips["s1a"])
        if need > room:
            base = int(rate.rstrip("%"))
            new = min(10, int(((1 + base / 100) * need / room - 1) * 100 + 1))
            for k in ("open", "s1a"):
                asyncio.run(tts(clean(tx[k]), voice, f"{new:+d}%", pitch, clips[k]))
            print("opening re-voiced at", f"{new:+d}%", round(need, 1), "->",
                  round(dur(clips["open"]) + dur(clips["s1a"]), 1), "room", round(room, 1), flush=True)

    # 2) placement
    place, warn, t_end = [], [], 0.0
    for i, k in enumerate(keys):
        d = dur(clips[k])
        if k == "open":
            t = 0.3
        elif k.startswith(("x_", "y_", "k_")):
            t = t_end + 1.0
        elif k in ("close", "final"):
            t = t_end + 0.9
        elif k == "s7b":
            t = t_end + 1.2
        elif k in img:
            t = max(img[k]["start"] + 0.35, t_end + 0.55)
        else:
            t = t_end + 0.8
        # next hard boundary = start of the next image after this line's image
        nxt = next((x for x in starts if x > t + 0.01), T)  # start of the next image
        room = nxt - t - 0.15
        f = clips[k]
        if d > room and k not in ("s7b", "close", "final"):
            tempo = min(1.12, d / max(room, 0.1))
            f2 = f"{OD}/{k}_t.wav"
            sh("ffmpeg", "-loglevel", "error", "-y", "-i", f, "-af", f"atempo={tempo:.3f}", f2)
            f, d = f2, dur(f2)
            if d > room:
                warn.append({"key": k, "type": "overrun", "seconds": round(d - room, 2)})
        place.append((k, f, t, d))
        t_end = t + d
    if t_end > T - 6:
        warn.append({"key": "final", "type": "ends_late", "end": round(t_end, 1), "video": T})

    gaps = []
    for (k1, _, t1, d1), (k2, _, t2, _) in zip(place, place[1:]):
        g = t2 - (t1 + d1)
        if g > 1.2:
            gaps.append({"after": k1, "before": k2, "seconds": round(g, 1)})

    # 3) mix to the video length, -14 LUFS, 1 s fade
    inputs, flt = [], []
    for j, (k, f, t, d) in enumerate(place):
        inputs += ["-i", f]
        ms = int(t * 1000)
        flt.append(f"[{j}]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{j}]")
    flt.append("".join(f"[v{j}]" for j in range(len(place))) +
               f"amix=inputs={len(place)}:normalize=0,apad=whole_dur={T},atrim=0:{T},"
               f"afade=t=out:st={T - 1}:d=1,loudnorm=I=-14:TP=-1.5:LRA=11[m]")
    track = f"{OD}/{EP}_{LANG}_free_{VER}.mp3"
    sh("ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(flt),
       "-map", "[m]", "-ar", "48000", "-b:a", "192k", track)
    lufs = subprocess.run(["ffmpeg", "-i", track, "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lufs)

    # 4) whisper check per line (H35): transcript vs text
    from faster_whisper import WhisperModel
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    norm = lambda s: re.sub(r"[^\w\s]", " ", s.lower()).split()
    checks = []
    for k, f, t, d in place:
        segs_w, _ = model.transcribe(f, language=LANG, beam_size=5)
        heard = " ".join(s.text for s in segs_w).strip()
        r = difflib.SequenceMatcher(None, norm(clean(tx[k])), norm(heard)).ratio()
        checks.append({"key": k, "start": round(t, 2), "dur": round(d, 2), "match": round(r, 3),
                       "heard": heard, "text": clean(tx[k])})
        print("asr", k, round(r, 3), flush=True)
    low = [c["key"] for c in checks if c["match"] < 0.85]

    rep = {"episode": EP, "lang": LANG, "voice": voice, "rate": rate, "pitch": pitch, "kid_pitch": KID_PITCH,
           "duration_video": T, "speech_end": round(t_end, 1), "lufs": m[-1] if m else None,
           "overruns": warn, "gaps_over_1_2s": gaps, "asr_below_0_85": low, "lines": checks,
           "status": "DRAFT – owner listens (H46.6); names test (H37); bs/sq human reviewer (H44.6)"}
    rp = f"{OD}/{EP}_{LANG}_free_{VER}_report.json"
    json.dump(rep, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sh("gh", "release", "upload", TAG, track, rp, "--repo", REPO, "--clobber")
    print(json.dumps({k: rep[k] for k in ("lang", "lufs", "speech_end", "overruns", "gaps_over_1_2s",
                                           "asr_below_0_85")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
