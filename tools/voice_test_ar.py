#!/usr/bin/env python3
"""Free Arabic voice samples (edge-tts neural voices) for the owner to pick by ear.
Same short passage (Yaqub s1a + s4c + s4d) for each voice -> release voice_test_ar."""
import asyncio, json, os, re, subprocess
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "belovedofallahkids/boa-render")
T = json.load(open(os.path.join(ROOT, "dub", "folge10_yaqub_ar.json")))
TEXT = "\n".join(T[k] for k in ("s1a", "s4c", "s4d"))
TEXT = re.sub(r"[﴾﴿]", "", TEXT)
VOICES = ["ar-SY-AmanyNeural", "ar-LB-LaylaNeural", "ar-JO-SanaNeural", "ar-SA-ZariyahNeural", "ar-EG-SalmaNeural"]

async def one(v, out):
    await edge_tts.Communicate(TEXT, v, rate="-8%", pitch="-4Hz").save(out)

def main():
    od = "/tmp/voice_test"; os.makedirs(od, exist_ok=True); files = []
    for i, v in enumerate(VOICES, 1):
        raw = os.path.join(od, f"raw_{i}.mp3"); out = os.path.join(od, f"probe_{i}_{v.split('-')[1]}_{v.split('-')[2].replace('Neural','')}.mp3")
        try:
            asyncio.run(one(v, raw))
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-b:a", "192k", out], check=True)
            files.append(out)
        except Exception as e:
            print("fail", v, e, flush=True)
    tag = "voice_test_ar"
    if subprocess.run(["gh", "release", "view", tag, "--repo", REPO], capture_output=True).returncode != 0:
        subprocess.run(["gh", "release", "create", tag, "--repo", REPO, "--title", tag, "--notes", "Arabische Stimmproben (kostenlos)"], check=True)
    subprocess.run(["gh", "release", "upload", tag, *files, "--repo", REPO, "--clobber"], check=True)
    print("\n".join(f"https://github.com/{REPO}/releases/download/{tag}/{os.path.basename(f)}" for f in files))

if __name__ == "__main__":
    main()
