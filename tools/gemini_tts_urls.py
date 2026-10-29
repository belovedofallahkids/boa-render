#!/usr/bin/env python3
"""Build free Gemini-TTS webhook links (Make 7996817, engine=tts) for script segments.
Usage: python3 tools/gemini_tts_urls.py scripts/folge15_harun.json s4b s6a ...
"""
import base64, json, re, sys, urllib.parse
import os
# Make webhook + key come from the environment (GitHub Secrets BOA_HOOK_URL / BOA_HOOK_KEY).
# Never write them into this repository: it is public.
HOOK = os.environ.get("BOA_HOOK_URL", "")
HOOK_KEY = os.environ.get("BOA_HOOK_KEY", "")
if not HOOK or not HOOK_KEY:
    raise SystemExit("BOA_HOOK_URL / BOA_HOOK_KEY not set (GitHub Secrets or local env)")
OMA = "Sulafat"
KID = "Puck"
STYLE = {"whispers": "whispering softly", "softly": "softly", "warmly": "warmly", "chuckles": "with a gentle chuckle",
         "curious": "curiously", "excited": "excitedly", "serious": "seriously", "sighs": "with a small sigh",
         "slowly": "slowly", "surprised": "surprised", "nervous": "a little nervously", "dramatically": "dramatically"}

def body(text, kid):
    tags = [t.strip() for t in re.findall(r"\[([^\]]+)\]", text)]
    clean = re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", " ", text)).strip()
    moods = ", ".join(STYLE[t] for t in tags if t in STYLE)
    if kid:
        lead = "Say this in German as a cheerful young boy, about 8 years old, " + (moods or "naturally")
    else:
        lead = ("Say this in German as a loving Arab grandmother in her late fifties telling a bedtime story "
                "to her grandsons, warm, calm, clear, " + (moods or "warmly"))
    return {"contents": [{"parts": [{"text": lead + ": " + clean}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": KID if kid else OMA}}}}}

def url(text, kid):
    b = base64.b64encode(json.dumps(body(text, kid), ensure_ascii=False).encode()).decode()
    return HOOK + "?" + urllib.parse.urlencode({"k": HOOK_KEY, "engine": "tts", "b": b})

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    out = {s: url(d["segments"][s], s in d["kids"]) for s in (sys.argv[2:] or d["segments"])}
    print(json.dumps(out, indent=1))
