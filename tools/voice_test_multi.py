#!/usr/bin/env python3
"""Free voice samples for every dub language (owner 30.10.2026: free voices, best per language).

Same passage per language (Yaqub: open + s1a + s4c, translated from the Arabic mother text).
Engines (all free, run on GitHub Actions):
  edge   – Microsoft neural voices (edge-tts)
  cb     – Chatterbox multilingual, cloned from Oma Karmoucha's German voice (en/fr/tr only)
-> release voice_test_multi: <lang>_<nr>_<engine>_<voice>.mp3 (-14 LUFS) + index.txt
"""
import asyncio, json, os, re, subprocess, traceback, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "belovedofallahkids/boa-render")
TAG = "voice_test_multi"
OMA_REF = ("https://storage.orshot.com/cloud/w-12325/renders/audio/"
           "boa_folge14_erzaehlung_komplett_2026-10-16mp3-hxXoUqUsSzs.mp3", 45.0, 56.5)

EDGE = {
    "en": ["en-US-AvaMultilingualNeural", "en-US-EmmaMultilingualNeural", "en-GB-SoniaNeural", "en-GB-LibbyNeural"],
    "fr": ["fr-FR-VivienneMultilingualNeural", "fr-FR-DeniseNeural", "fr-BE-CharlineNeural", "fr-CH-ArianeNeural"],
    "tr": ["tr-TR-EmelNeural", "en-US-AvaMultilingualNeural"],
    "bs": ["bs-BA-VesnaNeural", "hr-HR-GabrijelaNeural"],
    "sq": ["sq-AL-AnilaNeural"],
}
CB_LANGS = ["en", "fr", "tr"]


def text_for(lang):
    d = json.load(open(os.path.join(ROOT, "dub", f"folge10_yaqub_{lang}_from_ar_v1.json"), encoding="utf-8"))
    s = d.get("segments", d)
    t = " ".join(str(s[k]) for k in ("open", "s1a", "s4c") if k in s)
    t = re.sub(r"\[[^\]]*\]", "", t).replace("…", "...")
    return re.sub(r"\s+", " ", t).strip()


def norm(src, out):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", out], check=True)


async def edge_one(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="-8%").save(out)


def chatterbox(texts, od):
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    src = os.path.join(od, "ref_src.mp3")
    req = urllib.request.Request(OMA_REF[0], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
    open(src, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    ref = os.path.join(od, "ref.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ss", str(OMA_REF[1]),
                    "-to", str(OMA_REF[2]), "-ac", "1", "-ar", "24000", ref], check=True)
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    outs = []
    for lang in CB_LANGS:
        try:
            parts = [p for p in re.split(r"(?<=[.!?…»“\"])\s+", texts[lang]) if p.strip()]
            wavs = []
            for i, p in enumerate(parts):
                wv = model.generate(p, language_id=lang, audio_prompt_path=ref, cfg_weight=0.3, exaggeration=0.5)
                w = os.path.join(od, f"cb_{lang}_{i}.wav"); torchaudio.save(w, wv, model.sr); wavs.append(w)
            lst = os.path.join(od, f"cb_{lang}.txt")
            open(lst, "w").write("".join(f"file '{w}'\n" for w in wavs))
            raw = os.path.join(od, f"cb_{lang}.wav")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, raw], check=True)
            outs.append((lang, "cb", "OmaClone", raw))
            print("cb ok", lang, flush=True)
        except Exception:
            traceback.print_exc()
    return outs


def main():
    od = "/tmp/vtm"; os.makedirs(od, exist_ok=True)
    texts = {l: text_for(l) for l in EDGE}
    raws = []
    for lang, voices in EDGE.items():
        for v in voices:
            raw = os.path.join(od, f"edge_{lang}_{v}.mp3")
            try:
                asyncio.run(edge_one(texts[lang], v, raw)); raws.append((lang, "edge", v, raw))
            except Exception as e:
                print("edge fail", lang, v, e, flush=True)
    if os.environ.get("SKIP_CB") != "1":
        try:
            raws += chatterbox(texts, od)
        except Exception:
            traceback.print_exc()
    files, index, n = [], [], {}
    for lang, eng, v, raw in sorted(raws):
        n[lang] = n.get(lang, 0) + 1
        short = v.replace("Neural", "").replace("Multilingual", "Multi")
        out = os.path.join(od, f"{lang}_{n[lang]}_{eng}_{short}.mp3")
        norm(raw, out); files.append(out)
        index.append(f"{lang} {n[lang]}: {eng} {v}")
    idx = os.path.join(od, "index.txt"); open(idx, "w").write("\n".join(index) + "\n\nTEXT:\n" +
                                                              "\n".join(f"{l}: {t}" for l, t in texts.items()))
    files.append(idx)
    if subprocess.run(["gh", "release", "view", TAG, "--repo", REPO], capture_output=True).returncode != 0:
        subprocess.run(["gh", "release", "create", TAG, "--repo", REPO, "--title", TAG,
                        "--notes", "Kostenlose Stimmproben je Sprache (Yaqub-Passage)"], check=True)
    subprocess.run(["gh", "release", "upload", TAG, *files, "--repo", REPO, "--clobber"], check=True)
    print("\n".join(index))


if __name__ == "__main__":
    main()
