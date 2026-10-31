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
    "fr": ("fr-FR-VivienneMultilingualNeural", "-20%", "-2Hz"),  # owner 31.10.: French too fast
    "en": ("en-US-AvaMultilingualNeural", "-10%", "-2Hz"),
    "tr": ("tr-TR-EmelNeural", "-10%", "-3Hz"),
    "bs": ("bs-BA-VesnaNeural", "-15%", "-4Hz"),
    "sq": ("sq-AL-AnilaNeural", "-15%", "-4Hz"),
}
KID_PITCH = "+22Hz"
KIDFIX, SLOWED = [], []
OD = f"/tmp/dubfree_{LANG}"
VER = os.environ.get("DUB_VER") or ("v2" if os.environ.get("DUB_FILL") == "1" else "v1")


def sh(*a, **k):
    return subprocess.run(list(a), check=True, **k)


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]))


def clean(t):
    t = re.sub(r"\[[^\]]*\]", "", str(t)).replace("…", "... ")
    return re.sub(r"\s+", " ", t).strip()


def speak(t):
    """Text actually sent to TTS (owner 31.10.: «اخطاء كثيرة في الدبلجة»): tr-TR-Emel spells words with
    circumflexes as letters (Mûsâ -> 'M.S.', Hârûn -> 'H.R.N', Âşûrâ -> 'ÇR') -> plain letters for TTS only."""
    t = clean(t)
    if LANG == "tr":
        t = t.translate(str.maketrans("âîûÂÎÛ", "aiuAIU"))
    return t


async def tts(text, voice, rate, pitch, out):
    # H56 b4: edge-tts fails now and then (seen mostly in fr) -> retry with backoff instead of failing the whole track
    import edge_tts, asyncio as _a
    last = None
    for attempt in range(6):
        try:
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out)
            if os.path.exists(out) and os.path.getsize(out) > 1000:
                return
            last = RuntimeError("empty audio")
        except Exception as ex:
            last = ex
        print(f"tts retry {attempt + 1}: {last}", flush=True)
        await _a.sleep(5 * (attempt + 1))
    raise last


BACKUP = {"fr": "fr-FR-DeniseNeural", "en": "en-US-JennyNeural", "tr": "tr-TR-EmelNeural",
          "bs": "bs-BA-VesnaNeural", "sq": "sq-AL-AnilaNeural"}
FALLBACK = []


def main():
    os.makedirs(OD, exist_ok=True)
    tx = json.load(open(f"{ROOT}/dub/{EP}_{LANG}_from_ar_v1.json", encoding="utf-8"))
    import glob
    jf = os.environ.get("DUB_JOB") or sorted([x for x in glob.glob(f"{ROOT}/jobs/{EP}_v*.json") if re.search(r"_v\d+\.json$", x)],
                                              key=lambda x: int(re.findall(r"_v(\d+)\.json$", x)[0]))[-1]
    job = json.load(open(jf))
    segs = job["segments"]
    T = float(os.environ.get("DUB_DURATION") or 0)
    # H56 b11 (31.10.): track length = exact rendered video timeline (out/<job>/status.json); a track
    # shorter than the video failed YouTube processing (Yaqub 463.8 vs 469.8 s); raw audio length is
    # wrong when the job has audio_cuts (Ismail).
    stp = f"{ROOT}/out/{job['name'].replace('_keyed', '')}/status.json"
    if not T and os.path.exists(stp):
        T = float(json.load(open(stp)).get("timeline") or 0)
        print("video length from render status:", T, flush=True)
    if not T and job["segments"][-1].get("end") not in (None, "audio"):
        T = float(job["segments"][-1]["end"])
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
        p_ = KID_PITCH if (k in kids or k.startswith("k_")) else pitch
        try:
            asyncio.run(tts(speak(tx[k]), voice, rate, p_, out))
        except Exception as ex:  # H56 b9: deterministic NoAudioReceived on single lines -> safe fallbacks, logged
            txt = speak(tx[k]).replace("’", "'").replace("«", "").replace("»", "").replace("“", "").replace("”", "")
            done = False
            for v_, p2 in ((voice, p_), (voice, "+0Hz"), (BACKUP.get(LANG, voice), p_)):
                try:
                    asyncio.run(tts(txt, v_, rate, p2, out))
                    FALLBACK.append({"key": k, "voice": v_, "pitch": p2, "error": str(ex)[:120]})
                    done = True
                    break
                except Exception:
                    continue
            if not done:
                print("::error title=tts failed %s %s::%s" % (LANG, k, txt[:200]), flush=True)
                raise
        clips[k] = out
        print("tts", k, round(dur(out), 1), flush=True)

    # 1a) intensive check (owner 31.10.: «قم بمراجعة مكثفة»): one whisper model for everything; kid lines
    # (high pitch) are re-voiced at a lower pitch when the transcript does not match (fr «À la», en «Alice»)
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("DUB_ASR", "large-v3"), device="cpu", compute_type="int8")
    norm = lambda s_: re.sub(r"[^\w\s]", " ", s_.lower()).split()

    def match(k_, f_):
        sw, _ = model.transcribe(f_, language=LANG, beam_size=5)
        h = " ".join(x.text for x in sw).strip()
        return difflib.SequenceMatcher(None, norm(clean(tx[k_])), norm(h)).ratio(), h

    for k in keys:
        if not (k in kids or k.startswith("k_")):
            continue
        best = (match(k, clips[k])[0], clips[k], KID_PITCH)
        for p2 in ("+12Hz", "+6Hz"):
            if best[0] >= 0.9:
                break
            alt = f"{OD}/{k}_p{p2.strip('+Hz')}.mp3"
            try:
                asyncio.run(tts(speak(tx[k]), voice, rate, p2, alt))
            except Exception:
                continue
            r_ = match(k, alt)[0]
            if r_ > best[0]:
                best = (r_, alt, p2)
        if best[2] != KID_PITCH:
            KIDFIX.append({"key": k, "pitch": best[2], "match": round(best[0], 3)})
            clips[k] = best[1]
        print("kid", k, best[2], round(best[0], 3), flush=True)

    # 1b) opening fix (owner 30.10.: «صلح جملة البداية»): open + s1a share the first image and must end
    # before Ilyas's image (s1b). If too long, re-voice both at one faster rate (natural TTS, not atempo).
    if "open" in clips and "s1a" in clips and "s1b" in img:
        room = img["s1b"]["start"] - 0.3 - 0.55 - 0.25
        need = dur(clips["open"]) + dur(clips["s1a"])
        if need > room:
            base = int(rate.rstrip("%"))
            new = min(10, int(((1 + base / 100) * need / room - 1) * 100 + 1))
            for k in ("open", "s1a"):
                asyncio.run(tts(speak(tx[k]), voice, f"{new:+d}%", pitch, clips[k]))
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
        # an image that only continues the same sentence ("<key>|cont") is not a boundary for it
        same = set() if (k + "_2") in keys else {
            s_["start"] for s_ in segs if str(s_["script"]).split("|")[0] == k.split("_2")[0] and "|" in str(s_["script"])}
        nxt = next((x for x in starts if x > t + 0.01 and x not in same), T)  # start of the next image
        room = nxt - t - 0.15
        f = clips[k]
        # H56 b12 (31.10.): a gap/kid filler line (x_/y_/k_: no new info, H55) that cannot fit before the
        # next image even at max tempo is dropped for this language instead of pushing the story late
        if k.startswith(("x_", "y_", "k_")) and d / 1.12 > room:
            warn.append({"key": k, "type": "fill_skipped", "seconds": round(d / 1.12 - room, 2)})
            continue
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

    # 2b) no silences (owner 31.10.: «لا أريد سكتات إطلاقا»): (1) the line before a gap is slowed (>= 0.88);
    # (2) the remaining gap is filled from a bank of neutral Oma lines (dub/bank_neutral.json, no information,
    # H55/H58), never after the children fell asleep (s7a) or after the farewell.
    bank = json.load(open(f"{ROOT}/dub/bank_neutral.json", encoding="utf-8"))
    bclips, used = {}, {}
    for bk, bv in bank.items():
        if bk.startswith("_") or LANG not in bv:
            continue
        tx[bk] = bv[LANG]
        bclips[bk] = f"{OD}/{bk}.mp3"
        try:
            asyncio.run(tts(speak(bv[LANG]), voice, rate, pitch, bclips[bk]))
        except Exception:
            bclips.pop(bk)
    nofill = {"s7a", "s7b", "close", "final"}
    out_place = []
    for i, (k, f, t, d) in enumerate(place):
        nxt_t = place[i + 1][2] if i + 1 < len(place) else None
        if nxt_t is None or k in nofill:
            out_place.append((k, f, t, d))
            continue
        gap = nxt_t - (t + d)
        if gap > 1.0:
            nd = min(d / 0.88, d + gap - 0.6)
            if nd > d + 0.3:
                f2, tp = f"{OD}/{k}_slow.wav", d / nd
                sh("ffmpeg", "-loglevel", "error", "-y", "-i", f, "-af", f"atempo={tp:.4f}", f2)
                f, d = f2, dur(f2)
                SLOWED.append({"key": k, "tempo": round(tp, 3)})
        out_place.append((k, f, t, d))
        end = t + d
        gap = nxt_t - end
        while gap > 2.2:
            cand = [(dur(p_), b) for b, p_ in bclips.items()
                    if dur(p_) <= gap - 1.0 and end - used.get(b, -999) > 90]
            if not cand:
                break
            bd, b = max(cand)
            out_place.append((b, bclips[b], end + 0.5, bd))
            used[b] = end
            end += 0.5 + bd
            gap = nxt_t - end
    place = out_place
    t_end = max(t + d for _, _, t, d in place)

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
           "tts_fallbacks": FALLBACK, "kid_pitch_fix": KIDFIX, "slowed": SLOWED, "overruns": warn, "gaps_over_1_2s": gaps, "asr_below_0_85": low, "lines": checks,
           "status": "DRAFT – owner listens (H46.6); names test (H37); bs/sq human reviewer (H44.6)"}
    rp = f"{OD}/{EP}_{LANG}_free_{VER}_report.json"
    json.dump(rep, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sh("gh", "release", "upload", TAG, track, rp, "--repo", REPO, "--clobber")
    print(json.dumps({k: rep[k] for k in ("lang", "lufs", "speech_end", "overruns", "gaps_over_1_2s",
                                           "asr_below_0_85")}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # H56: logs are not readable from Claude sessions -> put the traceback into a GitHub annotation (API-readable)
        import traceback
        tb = traceback.format_exc()
        print("::error title=dub_free %s %s::%s" % (EP, LANG, tb[-1500:].replace("%", "%25").replace("\n", "%0A")), flush=True)
        raise
