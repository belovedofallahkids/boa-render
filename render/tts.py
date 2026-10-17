#!/usr/bin/env python3
"""Free TTS on GitHub Actions (no credits).

jobs/tts/<name>.json:
{"name": "...", "engines": ["chatterbox", "edge"],
 "ref_audio": "https://...mp3", "ref": [start, end], "kid_ref": [start, end],
 "edge_voice": "de-DE-SeraphinaMultilingualNeural", "edge_kid_voice": "de-DE-GiselaNeural",
 "lines": [{"id": "s4b", "text": "...", "kid": false}, ...]}
-> release tts_<name>: <engine>_<id>.mp3 and <engine>_alle.mp3 (lines joined with 0.6 s pauses)
-> out/tts/<name>/status.json
"""
import asyncio, glob, hashlib, json, os, re, subprocess, sys, traceback, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "belovedofallahkids/boa-render")
TAG = re.compile(r"\[[^\]]*\]")


def run(cmd):
    subprocess.run(cmd, check=True)


def clean(t):
    t = TAG.sub("", t).replace("…", "...")
    return re.sub(r"\s+", " ", t).strip()


def concat(files, out, gaps=None):
    lst = out + ".txt"
    parts = []
    for i, f in enumerate(files):
        g = 0.6 if gaps is None else gaps[i]
        if i > 0 and g > 0:
            sil = f"{out}_sil{i}.wav"
            run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(g), sil])
            parts.append(sil)
        w = f + ".24k.wav"
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", f, "-ar", "24000", "-ac", "1", w])
        parts.append(w)
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-b:a", "128k", out])


_ASR = None


def check(wav, sr, text, lang, wd):
    """Share of script words heard in the generated audio (faster-whisper small, CPU)."""
    global _ASR
    import difflib, torchaudio
    if _ASR is None:
        from faster_whisper import WhisperModel
        _ASR = WhisperModel("small", device="cpu", compute_type="int8")
    p = os.path.join(wd, "_chk.wav")
    torchaudio.save(p, wav, sr)
    segs, _ = _ASR.transcribe(p, language=lang, beam_size=1, vad_filter=False)
    norm = lambda t: [w for w in re.sub(r"[^\w\s]", " ", t.lower()).split() if w]
    a, b = norm(text), norm(" ".join(x.text for x in segs))
    if not a:
        return 1.0
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    return sum(n for _, _, n in sm.get_matching_blocks()) / len(a)


def chatterbox(job, wd):
    import torch, torchaudio
    _load = torch.load
    torch.load = lambda *a, **k: _load(*a, **{**k, "map_location": "cpu"})
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    src = os.path.join(wd, "ref_src.mp3")
    req = urllib.request.Request(job["ref_audio"], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
    with urllib.request.urlopen(req, timeout=180) as r, open(src, "wb") as f:
        f.write(r.read())
    refs = {}
    for key in ("ref", "kid_ref"):
        if key in job:
            a, b = job[key]
            p = os.path.join(wd, key + ".wav")
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ss", str(a), "-to", str(b), "-ar", "24000", "-ac", "1", p])
            refs[key] = p
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    outs = []
    report = []
    job["_report"] = report
    for ln in job["lines"]:
        ref = refs["kid_ref"] if ln.get("kid") and "kid_ref" in refs else refs["ref"]
        chunks, cur = [], ""
        for sent in re.split(r"(?<=[.!?…؟])\s+", clean(ln["text"])):
            if cur and len(cur) + len(sent) > 220:
                chunks.append(cur)
                cur = sent
            else:
                cur = (cur + " " + sent).strip()
        if cur:
            chunks.append(cur)
        pieces = []
        for c in chunks:
            best = None
            for attempt in range(4):
                wv = model.generate(c, language_id=job.get("lang", "de"), audio_prompt_path=ref,
                                    exaggeration=ln.get("exaggeration", 0.5), cfg_weight=ln.get("cfg", job.get("cfg", 0.3)))
                score = check(wv, model.sr, c, job.get("lang", "de"), wd)
                print(f"  {ln['id']} try {attempt+1} match {score:.2f}: {c[:50]}", flush=True)
                if best is None or score > best[0]:
                    best = (score, wv)
                if score >= 0.93:
                    break
            pieces.append(best[1])
            pieces.append(torch.zeros(1, int(model.sr * 0.35)))
            report.append({"id": ln["id"], "text": c, "match": round(best[0], 3)})
        wav = torch.cat(pieces[:-1], dim=1)
        w = os.path.join(wd, f"chatterbox_{ln['id']}.wav")
        torchaudio.save(w, wav, model.sr)
        m = w[:-4] + ".mp3"
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", w, "-b:a", "128k", m])
        outs.append(m)
        print("chatterbox", ln["id"], "ok", flush=True)
    return outs


def edge(job, wd):
    import edge_tts
    outs = []
    for ln in job["lines"]:
        v = job.get("edge_kid_voice") if ln.get("kid") else job.get("edge_voice")
        m = os.path.join(wd, f"edge_{ln['id']}.mp3")
        last = None
        for voice in [v, "de-DE-KatjaNeural", "de-DE-AmalaNeural"]:
            if not voice:
                continue
            try:
                asyncio.run(edge_tts.Communicate(clean(ln["text"]), voice).save(m))
                last = None
                break
            except Exception as e:
                last = f"{voice}: {e}"
                print("edge fail", ln["id"], last, flush=True)
        if last:
            raise RuntimeError(last)
        outs.append(m)
    return outs


def fetch(job, wd):
    outs = []
    for ln in job["lines"]:
        src = os.path.join(wd, f"fetch_{ln['id']}.src")
        req = urllib.request.Request(ln["url"], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
        with urllib.request.urlopen(req, timeout=300) as r, open(src, "wb") as f:
            f.write(r.read())
        m = os.path.join(wd, f"fetch_{ln['id']}.mp3")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-b:a", "128k", m])
        outs.append(m)
    return outs


def assemble(job, wd):
    """Lines with url + gap_before (s) -> one mp3 (44.1 kHz mono), loudness -16 LUFS."""
    parts = []
    for i, ln in enumerate(job["lines"]):
        src = os.path.join(wd, f"as_{i:02d}.src")
        req = urllib.request.Request(ln["url"], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
        with urllib.request.urlopen(req, timeout=300) as r, open(src, "wb") as f:
            f.write(r.read())
        g = float(ln.get("gap_before", 0))
        if g > 0:
            sil = os.path.join(wd, f"as_{i:02d}_gap.wav")
            run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(g), sil])
            parts.append(sil)
        w = os.path.join(wd, f"as_{i:02d}.wav")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ar", "44100", "-ac", "1", w])
        parts.append(w)
    lst = os.path.join(wd, "as_list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    raw = os.path.join(wd, "as_raw.wav")
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, raw])
    out = os.path.join(wd, job.get("out", job["name"]) + ".mp3")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", out])
    return [out]


def main():
    for jf in sorted(glob.glob(os.path.join(ROOT, "jobs", "tts", "*.json"))):
        raw = open(jf, "rb").read()
        h = hashlib.sha1(raw).hexdigest()
        job = json.loads(raw)
        name = job["name"]
        od = os.path.join(ROOT, "out", "tts", name)
        st = os.path.join(od, "status.json")
        if os.path.exists(st) and json.load(open(st)).get("hash") == h:
            continue
        os.makedirs(od, exist_ok=True)
        wd = os.path.join("/tmp", "tts_" + name)
        os.makedirs(wd, exist_ok=True)
        status = {"hash": h, "name": name, "results": {}}
        files = []
        for eng in job.get("engines", ["chatterbox"]):
            try:
                outs = {"chatterbox": chatterbox, "edge": edge, "fetch": fetch, "assemble": assemble}[eng](job, wd)
                if eng == "assemble":
                    files += outs
                else:
                    alle = os.path.join(wd, f"{eng}_alle.mp3")
                    gl = [ln.get("gap_before", 0.6) for ln in job["lines"]]
                    concat(outs, alle, gl)
                    files += outs + [alle]
                status["results"][eng] = "ok"
                if job.get("_report"):
                    status["check"] = job.pop("_report")
            except Exception:
                status["results"][eng] = traceback.format_exc()[-1500:]
        if files:
            tag = "tts_" + name
            ex = subprocess.run(["gh", "release", "view", tag, "--repo", REPO], capture_output=True).returncode == 0
            if ex:
                run(["gh", "release", "upload", tag, *files, "--clobber", "--repo", REPO])
            else:
                run(["gh", "release", "create", tag, *files, "--repo", REPO, "--title", tag, "--notes", "Kostenloser TTS-Test"])
            status["urls"] = {os.path.basename(f): f"https://github.com/{REPO}/releases/download/{tag}/{os.path.basename(f)}" for f in files}
        json.dump(status, open(st, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
