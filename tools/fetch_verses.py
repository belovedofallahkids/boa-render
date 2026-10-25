#!/usr/bin/env python3
"""Fetch approved meaning-translations (H44-أ/H51) verbatim from api.quran.com for given verse keys.
usage: fetch_verses.py <episode> <key,key,...>  -> dub/verses/<episode>.json"""
import json, sys, urllib.request, re
EP, KEYS = sys.argv[1], sys.argv[2].split(",")
WANT = {"fr": "hamidullah", "tr": "diyanet", "en": "saheeh", "bs": "korkut", "sq": "ahmeti"}
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "boa-render", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))
res = get("https://api.quran.com/api/v4/resources/translations")["translations"]
chosen = {}
for lang, key in WANT.items():
    cands = [t for t in res if (t.get("language_name") or "").lower().startswith({"fr":"fr","tr":"tu","en":"en","bs":"bo","sq":"al"}[lang]) and key in " ".join(str(t.get(f) or "") for f in ("author_name", "name", "slug", "language_name")).lower()]
    chosen[lang] = {"id": cands[0]["id"], "name": cands[0]["name"], "author": cands[0].get("author_name")} if cands else None
out = {"all_ids": [(t["id"], t.get("language_name"), t.get("author_name"), t.get("name")) for t in res if (t.get("language_name") or "").lower()[:2] in ("fr","tu","en","bo","al")], "source": "api.quran.com v4", "translations": chosen, "verses": {}}
for k in KEYS:
    v = get(f"https://api.quran.com/api/v4/verses/by_key/{k}?fields=text_uthmani")["verse"]
    e = {"ar": v["text_uthmani"]}
    for lang, c in chosen.items():
        if not c: continue
        t = get(f"https://api.quran.com/api/v4/quran/translations/{c['id']}?verse_key={k}")["translations"][0]["text"]
        e[lang] = re.sub(r"<sup.*?</sup>", "", t).strip()
    out["verses"][k] = e
json.dump(out, open(f"dub/verses/{EP}.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(chosen, ensure_ascii=False))
