"""Generate planned H59 images with Cloudflare Workers AI (free tier), same model as Make 7996817.
Reads prompts/h59_<ep>.json, generates every image with status "planned" exactly once (H15),
saves assets/h59/<ep>/<id>.jpg, marks status "generated" (NOT approved: Claude zoom-checks each
image before use, H36), and writes a check sheet (full + 4 quadrants) per image to out/h59_check/.
Secrets: CF_ACCOUNT_ID, CF_API_TOKEN. Env: EP (e.g. folge14_musa), MAX (default 40)."""
import base64, json, os, sys, time, requests, cv2, numpy as np
ep = os.environ["EP"]; mx = int(os.environ.get("MAX", "40"))
acc, tok = os.environ["CF_ACCOUNT_ID"], os.environ["CF_API_TOKEN"]
url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/@cf/black-forest-labs/flux-2-klein-4b"
p = f"prompts/h59_{ep}.json"; plan = json.load(open(p))
num = ep.split("_")[0].replace("folge", "folge")
outd = f"assets/h59/{num}"; os.makedirs(outd, exist_ok=True); os.makedirs("out/h59_check", exist_ok=True)
done = errs = 0
for im in plan["images"]:
    if im.get("status") != "planned" or done >= mx:
        continue
    r = requests.post(url, headers={"Authorization": f"Bearer {tok}"},
                      files={"prompt": (None, im["prompt"]), "width": (None, "1536"), "height": (None, "864")}, timeout=180)
    if r.status_code != 200:
        print("FAIL", im["id"], r.status_code, r.text[:300]); im["status"] = "failed"; im["error"] = r.text[:300]; errs += 1
        if r.status_code in (401, 403, 429): break
        continue
    b = base64.b64decode(r.json()["result"]["image"])
    a = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
    f = f"{outd}/{im['id']}.jpg"; cv2.imwrite(f, a, [cv2.IMWRITE_JPEG_QUALITY, 92])
    h, w = a.shape[:2]
    q = [a[:h//2, :w//2], a[:h//2, w//2:], a[h//2:, :w//2], a[h//2:, w//2:]]
    q = [cv2.resize(x, (768, 432)) for x in q]
    sheet = np.vstack([cv2.resize(a, (1536, 864)), np.hstack(q[:2]), np.hstack(q[2:])])
    cv2.imwrite(f"out/h59_check/{im['id']}.jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
    im.update(status="generated", file=f, source="Cloudflare flux-2-klein-4b (free)")
    done += 1; print("ok", im["id"]); time.sleep(1)
json.dump(plan, open(p, "w"), ensure_ascii=False, indent=1)
print("generated", done, "errors", errs)
