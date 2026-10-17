#!/usr/bin/env python3
"""Translate subs/*_de.srt into other languages with the free Gemini text model (via Make webhook).
-> subs/<name>_<lang>.srt (same numbers and times), status in out/subs/status.json"""
import base64, glob, hashlib, json, os, re, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = "https://hook.eu1.make.com/slmenq0wkshmnxiiq9sw393ucl46mj1y"
LANGS = {"ar": "Arabic (Modern Standard Arabic, simple words for children)", "en": "English", "tr": "Turkish",
         "fr": "French"}
NOTES = {
    "ar": "Use the Arabic Quranic names of the prophets (هارون، موسى، يونس ...). 'Friede sei mit ihm' = 'عليه السلام'. "
          "'Allah segne ihn und schenke ihm Frieden' = 'صلى الله عليه وسلم'. Allah = الله. Noah = نوح, Ilyas = إلياس, Oma = تيتا.",
    "en": "Keep 'Allah'. 'Friede sei mit ihm' = 'peace be upon him'. Muhammad formula = 'peace and blessings be upon him'. Oma = Grandma.",
    "tr": "Keep 'Allah'. Use Turkish prophet names (Harun, Musa, Yunus, İsa, Hz. Muhammed). 'Friede sei mit ihm' = '(a.s.)' written as 'aleyhisselam'. Oma = Babaanne.",
    "fr": "Keep 'Allah'. 'Friede sei mit ihm' = 'que la paix soit sur lui'. Muhammad formula = 'que la prière d'Allah et Son salut soient sur lui'. Oma = Mamie.",
}

def parse(srt):
    blocks = [b for b in re.split(r"\n\s*\n", srt.strip()) if b.strip()]
    out = []
    for b in blocks:
        l = b.strip().split("\n")
        out.append((l[0].strip(), l[1].strip(), "\n".join(l[2:]).strip()))
    return out

def ask(prompt, model="gemini-3.5-flash"):
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    payload = json.dumps({"k": "boaFlux2026x", "engine": "text", "m": model,
                          "b": base64.b64encode(json.dumps(body, ensure_ascii=False).encode()).decode()}).encode()
    req = urllib.request.Request(HOOK, data=payload, headers={"Content-Type": "application/json", "User-Agent": "boa-render"})
    with urllib.request.urlopen(req, timeout=320) as r:
        d = json.loads(r.read())
    return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])

def main():
    os.makedirs(os.path.join(ROOT, "out", "subs"), exist_ok=True)
    stp = os.path.join(ROOT, "out", "subs", "status.json")
    status = json.load(open(stp)) if os.path.exists(stp) else {}
    for f in sorted(glob.glob(os.path.join(ROOT, "subs", "*_de.srt"))):
        src = open(f).read(); h = hashlib.sha1(src.encode()).hexdigest()
        base = os.path.basename(f)[:-7]
        cues = parse(src)
        for lang, lname in LANGS.items():
            key = f"{base}_{lang}"
            outp = os.path.join(ROOT, "subs", key + ".srt")
            if status.get(key, {}).get("hash") == h and os.path.exists(outp):
                continue
            numbered = "\n".join(f"[{n}] {t.replace(chr(10), ' ')}" for n, _, t in cues)
            prompt = (f"Translate these German subtitle lines of a children's Islamic bedtime story into {lname}. "
                      f"{NOTES[lang]} Keep the meaning exact and respectful; do not add or remove anything. "
                      f"Return exactly one line per input line, in the same order, each starting with the same [number]. "
                      f"No other text.\n\n{numbered}")
            err = None
            for attempt in range(3):
                try:
                    txt = ask(prompt)
                    got = dict(re.findall(r"^\[(\d+)\]\s*(.+)$", txt, flags=re.M))
                    missing = [n for n, _, _ in cues if n not in got]
                    if missing:
                        raise ValueError(f"missing {missing[:5]}")
                    blocks = [f"{n}\n{tm}\n{got[n].strip()}\n" for n, tm, _ in cues]
                    open(outp, "w").write("\n".join(blocks))
                    status[key] = {"hash": h, "ok": True, "cues": len(cues)}
                    err = None
                    break
                except Exception as e:
                    err = str(e)[:500]
                    time.sleep(20)
            if err:
                status[key] = {"hash": h, "ok": False, "error": err}
            print(key, status[key], flush=True)
            json.dump(status, open(stp, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
