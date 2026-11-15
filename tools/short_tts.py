#!/usr/bin/env python3
"""Free TTS lines for a Short (edge-tts, same voices as dub_free.py), prophet names in each
language's own form (owner 13.11.2026, names/names_local.json). Input: jobs/short_tts/<name>.json
{"ep": "folge14_musa", "keys": [...], "kids": [...], "langs": ["en","fr"]}. Output: /tmp/out/<lang>_<key>.mp3"""
import asyncio, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
job = json.load(open(sys.argv[1], encoding="utf-8"))
NL = json.load(open(f"{ROOT}/names/names_local.json", encoding="utf-8"))
VOICE = {"fr": ("fr-FR-VivienneMultilingualNeural", "-20%", "-2Hz"),
         "en": ("en-US-AvaMultilingualNeural", "-10%", "-2Hz")}
KID = "+22Hz"
os.makedirs("/tmp/out", exist_ok=True)

def clean(t):
    t = re.sub(r"\[[^\]]*\]", "", str(t)).replace("…", "... ")
    return re.sub(r"\s+", " ", t).strip()

def loc(t, L):
    nl = NL.get(L, {})
    for a in sorted(nl, key=len, reverse=True):
        t = re.sub(r"(?<![\w’'])" + re.escape(a) + r"(?![\w])", nl[a], t)
    return t

async def tts(text, voice, rate, pitch, out):
    import edge_tts
    last = None
    for i in range(6):
        try:
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out)
            if os.path.getsize(out) > 1000:
                return
        except Exception as ex:
            last = ex
        await asyncio.sleep(5 * (i + 1))
    raise RuntimeError(f"tts failed: {last}")

texts = {}
for L in job["langs"]:
    tx = json.load(open(f"{ROOT}/dub/{job['ep']}_{L}_from_ar_v1.json", encoding="utf-8"))
    v, r, p = VOICE[L]
    for k in job["keys"]:
        t = loc(clean(tx[k]), L)
        texts[f"{L}_{k}"] = t
        asyncio.run(tts(t, v, r, KID if k in job.get("kids", []) else p, f"/tmp/out/{L}_{k}.mp3"))
        print(L, k, t, flush=True)
json.dump(texts, open("/tmp/out/texts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
