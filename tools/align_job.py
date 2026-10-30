"""Key an old render job (episodes 1-9, segments without "script") to the German script keys.
Free, runs on GitHub Actions: faster-whisper word timestamps on the job's German narration audio,
then each key (s1a, s1b, ...) is found in order by its first words; every image segment gets
script = the key speaking at its start ("key" if the key starts in it, else "key|cont").
Input : jobs/<job>.json  +  dub/align/<ep>_de_keys.json  ({"s1a": "German text", ...} in order)
Output: jobs/<job>_keyed.json  + dub/align/<ep>_align_report.json
"""
import json, os, re, subprocess, sys, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP, JOB = os.environ["ALIGN_EP"], os.environ["ALIGN_JOB"]

def norm(w):
    return re.sub(r"[^a-zäöüß0-9]", "", w.lower())

def main():
    job = json.load(open(f"{ROOT}/jobs/{JOB}.json"))
    keys = json.load(open(f"{ROOT}/dub/align/{EP}_de_keys.json"))
    keys = {k: v for k, v in keys.items() if not k.startswith("_")}
    subprocess.run(["curl", "-sSL", "-o", "/tmp/a.mp3", job["audio"]], check=True)
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe("/tmp/a.mp3", language="de", word_timestamps=True, beam_size=5)
    words = [(norm(w.word), w.start) for s in segs for w in s.words if norm(w.word)]
    seq = [w for w, _ in words]
    starts, pos, rep = {}, 0, {}
    for k, text in keys.items():
        tw = [norm(x) for x in re.sub(r"\[[^\]]*\]", " ", text).split() if norm(x)][:6]
        best, bi = 0.0, None
        for i in range(pos, min(len(seq), pos + 400)):
            r = difflib.SequenceMatcher(None, tw, seq[i:i + len(tw)]).ratio()
            if r > best:
                best, bi = r, i
            if r == 1.0:
                break
        if bi is None or best < 0.5:
            rep[k] = {"found": False, "score": round(best, 2)}
            continue
        starts[k] = words[bi][1]
        pos = bi + 1
        rep[k] = {"found": True, "t": round(words[bi][1], 2), "score": round(best, 2)}
    order = sorted(starts.items(), key=lambda x: x[1])
    used = set()
    for s in job["segments"]:
        cur = None
        for k, t in order:
            if t <= s["start"] + 1.0:
                cur = k
        if cur is None:
            cur = order[0][0]
        if cur in used and not any(abs(t - s["start"]) < 1.0 for k, t in order if k == cur):
            s["script"] = f"{cur}|cont"
        else:
            s["script"] = cur
        used.add(cur)
    out = dict(job, name=JOB + "_keyed")
    json.dump(out, open(f"{ROOT}/jobs/{JOB}_keyed.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"episode": EP, "job": JOB, "keys": rep, "segments": [(s["start"], s["label"], s["script"]) for s in job["segments"]]},
              open(f"{ROOT}/dub/align/{EP}_align_report.json", "w"), ensure_ascii=False, indent=1)
    miss = [k for k, v in rep.items() if not v["found"]]
    print("keys found", len(starts), "/", len(keys), "missing", miss)

if __name__ == "__main__":
    main()
