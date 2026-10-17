#!/usr/bin/env python3
"""Free dubbing: translate script segments (Gemini via Make) -> Chatterbox in Oma's voice -> fit to German timing.
jobs/dub/<episode>.json (tools/dub_job.py) -> dub/<episode>_<lang>.json (texts), release dub_<episode>: <episode>_<lang>.mp3
status out/dub/<episode>/status.json"""
import glob, hashlib, json, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translate import ask
import tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "belovedofallahkids/boa-render")
LN = {"ar": "Arabic (Modern Standard Arabic, simple and warm, for small children)", "en": "English", "tr": "Turkish", "fr": "French"}
NOTE = {
    "ar": "Use Quranic Arabic names (هارون، موسى، إلياس، نوح). 'Friede sei mit ihm' = 'عليه السلام'; Muhammad formula = 'صلى الله عليه وسلم'. Oma calls the boys 'يا حبيبي'. Add full tashkeel (diacritics) on every word so a speech engine reads it correctly.",
    "en": "Keep 'Allah'. 'Friede sei mit ihm' = 'peace be upon him'. Muhammad formula = 'peace and blessings be upon him'. 'mein Schatz' = 'my darling'.",
    "tr": "Keep 'Allah'. Turkish prophet names (Harun, Musa, Hz. Muhammed). 'Friede sei mit ihm' = 'aleyhisselam'.",
    "fr": "Keep 'Allah'. 'Friede sei mit ihm' = 'que la paix soit sur lui'.",
}

def run(c):
    subprocess.run(c, check=True)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())

def translate(job, lang):
    clean = lambda t: re.sub(r"\[[^\]]*\]", "", t).strip()
    lines = "\n".join("[" + s["id"] + "] " + clean(s["de"]) for s in job["segments"])
    prompt = (f"Translate this German children's Islamic bedtime story (grandmother Oma telling her grandsons Noah and Ilyas "
              f"about Prophet {job['prophet']}) into {LN[lang]}. {NOTE[lang]} Keep meaning exact, add or remove nothing, keep it natural "
              f"for speaking aloud and about the same length. Return one line per input line, same order, each starting with the same [id]. No other text.\n\n{lines}")
    last = ""
    for a, model in enumerate(["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"]):
        try:
            txt = ask(prompt, model)
            got = dict(re.findall(r"^\s*\**\[(s\d+[a-z])\]\**\s*(.+)$", txt, flags=re.M))
            miss = [s["id"] for s in job["segments"] if s["id"] not in got]
            if not miss:
                return got
            last = f"{model}: missing {miss[:6]} | {txt[:400]}"
        except Exception as e:
            last = f"{model}: {e}"
        print("translate fail", last, flush=True)
        time.sleep(40)
    raise RuntimeError("translation incomplete: " + last)

def main():
    for jf in sorted(glob.glob(os.path.join(ROOT, "jobs", "dub", "*.json"))):
        raw = open(jf, "rb").read(); h = hashlib.sha1(raw).hexdigest(); job = json.loads(raw)
        ep = job["episode"]; od = os.path.join(ROOT, "out", "dub", ep); st = os.path.join(od, "status.json")
        status = json.load(open(st)) if os.path.exists(st) else {}
        os.makedirs(od, exist_ok=True); os.makedirs(os.path.join(ROOT, "dub"), exist_ok=True)
        wd = "/tmp/dub_" + ep; os.makedirs(wd, exist_ok=True)
        files = []
        for lang in job["langs"]:
            if status.get(lang, {}).get("hash") == h and status[lang].get("ok"):
                continue
            try:
                tp = os.path.join(ROOT, "dub", f"{ep}_{lang}.json")
                texts = json.load(open(tp)) if os.path.exists(tp) else translate(job, lang)
                json.dump(texts, open(tp, "w"), indent=1, ensure_ascii=False)
                tj = {"name": f"{ep}_{lang}", "lang": lang, "cfg": 0.3, "ref_audio": job["ref_audio"], "ref": job["ref"],
                      "kid_ref": job["kid_ref"],
                      "lines": [{"id": s["id"], "text": texts[s["id"]], "kid": s["kid"]} for s in job["segments"]]}
                lwd = os.path.join(wd, lang); os.makedirs(lwd, exist_ok=True)
                outs = tts.chatterbox(tj, lwd)
                rep = tj.get("_report", [])
                # fit to German timing
                parts, cur, fit = [], 0.0, []
                segs = job["segments"]
                for i, (s, f) in enumerate(zip(segs, outs)):
                    nxt = segs[i + 1]["start"] if i + 1 < len(segs) else job["duration"]
                    slot = max(0.8, nxt - s["start"] - 0.3)
                    d = dur(f); tempo = 1.0
                    if d > slot:
                        tempo = min(1.3, d / slot)
                    w = os.path.join(lwd, f"fit_{s['id']}.wav")
                    run(["ffmpeg", "-loglevel", "error", "-y", "-i", f, "-af", f"atempo={tempo:.3f}", "-ar", "44100", "-ac", "1", w])
                    d2 = dur(w)
                    pad = s["start"] - cur
                    if pad > 0.02:
                        sp = os.path.join(lwd, f"pad_{s['id']}.wav")
                        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{pad:.3f}", sp])
                        parts.append(sp); cur += pad
                    parts.append(w); cur += d2
                    fit.append({"id": s["id"], "tempo": round(tempo, 3), "drift": round(cur - (s["start"] + d2), 2)})
                tail = job["duration"] + 6.0 - cur
                if tail > 0.02:
                    sp = os.path.join(lwd, "pad_end.wav")
                    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{tail:.3f}", sp])
                    parts.append(sp)
                lst = os.path.join(lwd, "list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
                raw_w = os.path.join(lwd, "raw.wav")
                run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, raw_w])
                out = os.path.join(wd, f"{ep}_{lang}.mp3")
                run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw_w, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", out])
                files.append(out)
                status[lang] = {"hash": h, "ok": True, "duration": round(dur(out), 2), "fit": fit, "check": rep}
            except Exception as e:
                import traceback
                status[lang] = {"hash": h, "ok": False, "error": traceback.format_exc()[-1500:]}
            json.dump(status, open(st, "w"), indent=1, ensure_ascii=False)
        if files:
            tag = "dub_" + ep
            ex = subprocess.run(["gh", "release", "view", tag, "--repo", REPO], capture_output=True).returncode == 0
            run(["gh", "release", "upload" if ex else "create", tag, *files, "--repo", REPO] + (["--clobber"] if ex else ["--title", tag, "--notes", "Synchronisation (kostenlos)"]))
            for f in files:
                lang = f.rsplit("_", 1)[1][:-4]
                status[lang]["url"] = f"https://github.com/{REPO}/releases/download/{tag}/{os.path.basename(f)}"
            json.dump(status, open(st, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
