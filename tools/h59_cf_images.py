"""Generate planned H59 images with Cloudflare Workers AI (free tier), same model as Make 7996817.
Reads prompts/h59_<ep>.json, generates every image with status "planned" exactly once (H15),
saves assets/h59/<ep>/<id>.jpg, marks status "generated" (NOT approved: Claude zoom-checks each
image before use, H36), and writes a check sheet (full + 4 quadrants) per image to out/h59_check/.
Secrets: CF_ACCOUNT_ID, CF_API_TOKEN. Env: EP (e.g. folge14_musa), MAX (default 40)."""
import base64, json, os, sys, time, requests, cv2, numpy as np
ep = os.environ["EP"]; mx = int(os.environ.get("MAX", "40"))
acc, tok = os.environ["CF_ACCOUNT_ID"].strip(), os.environ["CF_API_TOKEN"].strip()
import requests as _rq
for _u in ("https://api.cloudflare.com/client/v4/user/tokens/verify", f"https://api.cloudflare.com/client/v4/accounts/{acc}/tokens/verify"):
    _r = _rq.get(_u, headers={"Authorization": f"Bearer {tok}"}, timeout=30)
    print("CHECK", _u.split("/v4/")[1].split("/")[0], _r.status_code, (_r.json().get("result") or {}).get("status"), [e.get("message") for e in _r.json().get("errors", [])])
print("CHECK acc_len", len(acc), "acc_hex", all(c in "0123456789abcdef" for c in acc), "tok_len", len(tok))
url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/@cf/black-forest-labs/flux-2-klein-4b"
p = f"prompts/h59_{ep}.json"; plan = json.load(open(p))
num = ep.split("_")[0].replace("folge", "folge")
outd = f"assets/h59/{num}"; os.makedirs(outd, exist_ok=True); os.makedirs("out/h59_check", exist_ok=True)
done = errs = 0

cf_dead = False
_pol_last = 0.0
HOOK, HOOK_KEY = os.environ.get("BOA_HOOK_URL", ""), os.environ.get("BOA_HOOK_KEY", "")
def _ok(b):
    try: return b is not None and cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR) is not None
    except Exception: return False
def fallback(prompt):
    """Free fallbacks when the Cloudflare daily quota is used up: Gemini image models via the Make hook, then Pollinations (free, no key)."""
    if HOOK and HOOK_KEY:
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
        for m in ("gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-3.1-flash-image-preview", "gemini-2.0-flash-preview-image-generation"):
            try:
                r = requests.post(HOOK, json={"k": HOOK_KEY, "engine": "text", "m": m,
                                  "b": base64.b64encode(json.dumps(body).encode()).decode()}, timeout=240)
                j = r.json()
                for part in j["candidates"][0]["content"]["parts"]:
                    d = (part.get("inlineData") or {}).get("data")
                    if d and _ok(base64.b64decode(d)): print("FALLBACK gemini", m); return base64.b64decode(d), f"Gemini {m} (free tier, via Make)"
                print("GEM_FAIL", m, r.status_code, r.text[:200])
            except Exception as e:
                print("GEM_FAIL", m, str(e)[:200])
    import urllib.parse, re
    global _pol_last
    for t in range(6):
        wait = 50 - (time.time() - _pol_last)
        if wait > 0: time.sleep(wait)
        try:
            _pol_last = time.time()
            r = requests.get("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt),
                             params={"width": 1536, "height": 864, "model": "flux", "nologo": "true", "seed": 11 + t}, timeout=240)
            if r.status_code == 200 and _ok(r.content):
                a = cv2.imdecode(np.frombuffer(r.content, np.uint8), cv2.IMREAD_COLOR)
                h, w = a.shape[:2]; nh = int(h * 0.90); nw = int(nh * 16 / 9)   # cut off bottom strip with the pollinations logo
                x0 = max(0, (w - nw) // 2); a = cv2.resize(a[:nh, x0:x0 + nw], (1536, 864), interpolation=cv2.INTER_LANCZOS4)
                print("FALLBACK pollinations flux"); return cv2.imencode(".jpg", a, [cv2.IMWRITE_JPEG_QUALITY, 94])[1].tobytes(), "Pollinations flux (free, logo strip cropped)"
            print("POL_FAIL", r.status_code, r.text[:150])
            m = re.search(r"Retry after (\d+)s", r.text)
            if m: _pol_last = time.time() - 50 + int(m.group(1)) + 3
        except Exception as e:
            print("POL_FAIL", str(e)[:150])
    return None, None
for im in plan["images"]:
    if im.get("status") != "planned" or done >= mx:
        continue
    b, src = None, "Cloudflare flux-2-klein-4b (free)"
    if not cf_dead:
        r = requests.post(url, headers={"Authorization": f"Bearer {tok}"},
                          files={"prompt": (None, im["prompt"]), "width": (None, "1536"), "height": (None, "864")}, timeout=180)
        if r.status_code == 200:
            b = base64.b64decode(r.json()["result"]["image"])
        else:
            print("CF_FAIL", im["id"], r.status_code, r.text[:200])
            if "4006" in r.text or r.status_code in (401, 403, 429): cf_dead = True
    if b is None:
        b, src = fallback(im["prompt"])
    if b is None:
        im["status"] = "failed"; im["error"] = "all free engines failed"; errs += 1; print("FAIL", im["id"]); continue
    a = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
    f = f"{outd}/{im['id']}.jpg"; cv2.imwrite(f, a, [cv2.IMWRITE_JPEG_QUALITY, 92])
    h, w = a.shape[:2]
    q = [a[:h//2, :w//2], a[:h//2, w//2:], a[h//2:, :w//2], a[h//2:, w//2:]]
    q = [cv2.resize(x, (768, 432)) for x in q]
    sheet = np.vstack([cv2.resize(a, (1536, 864)), np.hstack(q[:2]), np.hstack(q[2:])])
    cv2.imwrite(f"out/h59_check/{im['id']}.jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
    im.update(status="generated", file=f, source=src)
    done += 1; print("ok", im["id"]); time.sleep(1)
json.dump(plan, open(p, "w"), ensure_ascii=False, indent=1)
print("generated", done, "errors", errs)
