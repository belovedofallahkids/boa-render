#!/usr/bin/env python3
"""German subtitles (SRT) from the script text, timed by the word transcript.
Usage: python3 tools/subs.py scripts/folge15_harun.json out/transcripts/folge15_harun_ton.json subs/folge15_harun_de.srt
Script spelling is kept (Ilyas, Dhul-Kifl, Allah ...), only the timing comes from whisper."""
import difflib, json, re, sys

def norm(w):
    return re.sub(r"[^a-zäöüß0-9]", "", w.lower())

def tc(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def wrap(text, width=42):
    if len(text) <= width:
        return text
    words = text.split(); best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best[0]:
            best = (score, a + "\n" + b)
    return best[1]

def main(script, transcript, out):
    d = json.load(open(script)); tr = json.load(open(transcript))
    tw = [(w["start"], w["end"], norm(w["word"])) for s in tr["segments"] for w in s["words"] if norm(w["word"])]
    toks = []  # (orig token, seg id)
    for sid, t in d["segments"].items():
        t = re.sub(r"\[[^\]]*\]", " ", t).replace("…", "…")
        for tok in t.split():
            toks.append(tok)
    nums = {"vierzig": "40", "hundert": "100", "dreiundzwanzig": "23"}
    sw = [nums.get(norm(t), norm(t)) for t in toks]
    keep = [i for i, w in enumerate(sw) if w]
    sm = difflib.SequenceMatcher(a=[sw[i] for i in keep], b=[w[2] for w in tw], autojunk=False)
    times = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            times[keep[a + k]] = (tw[b + k][0], tw[b + k][1])
    # interpolate unmatched
    idx = sorted(times)
    for i in range(len(toks)):
        if i in times:
            continue
        prev = max([j for j in idx if j < i], default=None); nxt = min([j for j in idx if j > i], default=None)
        s = times[prev][1] if prev is not None else 0.0
        e = times[nxt][0] if nxt is not None else s + 0.4
        times[i] = (s, max(s + 0.1, e))
    # cues: split at sentence ends, long ones at commas
    cues, cur = [], []
    for i, tok in enumerate(toks):
        cur.append(i)
        text = " ".join(toks[j] for j in cur)
        end_sent = re.search(r"[.!?…:]$", tok)
        if (end_sent and len(text) > 15) or (len(text) > 70 and tok.endswith(",")) or len(text) > 80:
            cues.append(cur); cur = []
    if cur:
        cues.append(cur)
    lines = []
    for n, c in enumerate(cues):
        s = times[c[0]][0]; e = times[c[-1]][1] + 0.25
        if n + 1 < len(cues):
            e = min(e, times[cues[n + 1][0]][0] - 0.05)
        e = max(e, s + 1.0)
        text = " ".join(toks[j] for j in c).strip(" …")
        lines.append(f"{n+1}\n{tc(s)} --> {tc(e)}\n{wrap(text)}\n")
    open(out, "w").write("\n".join(lines))
    print(out, len(lines), "cues, matched", f"{len(times and [k for k in keep if k in dict(times)])}/{len(keep)}")

if __name__ == "__main__":
    main(*sys.argv[1:4])
