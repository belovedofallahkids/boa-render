#!/usr/bin/env python3
"""Second reviewer for scripts (free Gemini text model via Make): Islamic accuracy, invented details, child safety.
scripts/folgeNN_*.json -> reviews/folgeNN_<key>.md ; skips unchanged scripts."""
import base64, glob, hashlib, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translate import ask  # same webhook
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = ("Rules of the channel: German Islamic bedtime stories for children 4-12. Every sentence must be supported by the Quran "
         "or a sahih/hasan hadith (or clearly marked tafsir); nothing invented, nothing from weak or Israiliyat sources stated as fact. "
         "Prophets, angels, Maryam and the Prophet Muhammad are never depicted in images. No idols shown. Violence only hinted, gentle for children. "
         "The narrator is the grandmother Oma; Noah (8) and Ilyas (10) are her grandsons and ask questions.")

def main():
    os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
    for f in sorted(glob.glob(os.path.join(ROOT, "scripts", "folge*.json"))):
        raw = open(f).read(); h = hashlib.sha1(raw.encode()).hexdigest()[:12]
        d = json.loads(raw)
        out = os.path.join(ROOT, "reviews", os.path.basename(f)[:-5] + ".md")
        if os.path.exists(out) and h in open(out).read(300):
            continue
        lines = "\n".join(f"[{k}] {v}" for k, v in d["segments"].items())
        src = "\n".join(f"[{k}] {v}" for k, v in d.get("sources", {}).items())
        imgs = "\n".join(f"- {k}: {v}" for k, v in d.get("images", {}).items())
        prompt = (f"You are a careful reviewer with knowledge of Quran, hadith and tafsir. {RULES}\n\n"
                  f"Episode {d['nr']}: Prophet {d['prophet']}.\n\nSCRIPT (German):\n{lines}\n\nCLAIMED SOURCES:\n{src}\n\nIMAGE PROMPTS:\n{imgs}\n\n"
                  "Check sentence by sentence. Report ONLY real problems, each as a bullet: [segment id] problem - why - "
                  "suggested German fix. Categories: (1) not in Quran/sahih hadith or wrong reference, (2) factual error, "
                  "(3) not suitable for small children, (4) image prompt that could depict a prophet/person/idol, "
                  "(5) German language error. If a category has no problem, write 'keine'. Answer in German. End with an overall score out of 10.")
        try:
            txt = ask(prompt)
        except Exception as e:
            txt = f"FEHLER: {e}"
        open(out, "w").write(f"<!-- {h} -->\n# Zweite Prüfung (Gemini) – Folge {d['nr']} {d['prophet']}\n\n{txt}\n")
        print(out, flush=True)
        time.sleep(5)

if __name__ == "__main__":
    main()
