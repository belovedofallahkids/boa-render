#!/usr/bin/env python3
"""Build Cloudflare-FLUX webhook links (Make scenario 7996817) from a prompt list.

Usage: python3 tools/cf_urls.py prompts/folge10.json
File: {"episode": "folge10", "images": {"name": "scene text", ...}, "animals_ok": ["name", ...]}
Every prompt gets the series style in front and the safety rules at the end (H-rules: no people,
no faces, no text; never domes/minarets/crosses unless the scene needs nothing of the kind).
"""
import json
import os
import sys
import urllib.parse

# Make webhook + key come from the environment (GitHub Secrets BOA_HOOK_URL / BOA_HOOK_KEY).
# Never write them into this repository: it is public.
HOOK = os.environ.get("BOA_HOOK_URL", "")
HOOK_KEY = os.environ.get("BOA_HOOK_KEY", "")
if not HOOK or not HOOK_KEY:
    raise SystemExit("BOA_HOOK_URL / BOA_HOOK_KEY not set (GitHub Secrets or local env)")
PRE = ("Stylized Pixar 3D animated movie look, soft rounded shapes, warm saturated colors, "
       "not photorealistic. ")
SUF_PEOPLE = " Family animated film still. No people, no human figures, no faces, no hands, no text, no letters."
SUF_ANIMALS = " No animals."
SUF_ARCH = " No domes, no minarets, no towers, no crosses."


def main():
    spec = json.load(open(sys.argv[1]))
    out = {}
    for name, scene in spec["images"].items():
        p = PRE + scene.strip()
        if name not in spec.get("animals_ok", []):
            p += SUF_ANIMALS
        p += SUF_ARCH + SUF_PEOPLE
        out[name] = HOOK + "?" + urllib.parse.urlencode({"k": HOOK_KEY, "prompt": p})
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
