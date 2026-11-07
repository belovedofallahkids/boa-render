#!/usr/bin/env python3
"""Folge 16 Dhul-Kifl: (narration) 19 Oma lines -> one narration mp3 + word transcript;
(imgcheck) every plan image as full view + 4 quarters for the rules 5-8 check."""
import json, os, subprocess, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
S = json.load(open(os.path.join(ROOT, "scripts", "folge16_dhulkifl.json")))
REL = "https://github.com/belovedofallahkids/boa-render/releases/download/dub_de_folge16_dhulkifl_oma/"
W = os.path.join(ROOT, "work16"); os.makedirs(W, exist_ok=True)
def sh(*c): subprocess.run(c, check=True)

def narration():
    order = list(S["segments"])
    parts = []
    for i, k in enumerate(order):
        f = f"{W}/{k}.mp3"; urllib.request.urlretrieve(REL + k + ".mp3", f)
        t = f"{W}/{k}.wav"
        # trim leading/trailing silence of each take
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", f, "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse",
           "-ar", "44100", "-ac", "1", t)
        parts.append(t)
        if i + 1 < len(order):
            nxt = order[i + 1]
            gap = 1.1 if nxt[:2] != k[:2] else (0.6 if (k in S["kids"] or nxt in S["kids"]) else 0.8)
            g = f"{W}/gap_{k}.wav"
            sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(gap), g)
            parts.append(g)
    lst = f"{W}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    out = f"{W}/folge16_dhulkifl_de.mp3"
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", out)
    from faster_whisper import WhisperModel
    m = WhisperModel("medium", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(out, language="de", word_timestamps=True,
                           initial_prompt="Oma erzählt Noah und Ilyas vom Propheten Dhul-Kifl. Ismail, Idris, Al-Yasa, Dawud.")
    os.makedirs(os.path.join(ROOT, "out", "transcripts"), exist_ok=True)
    rows, txt = [], []
    for s in segs:
        txt.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        for w in s.words:
            rows.append(f"{w.start:.3f} {w.end:.3f} {w.word.strip()}")
    open(os.path.join(ROOT, "out", "transcripts", "folge16_dhulkifl_ton.txt"), "w").write("\n".join(rows) + "\n")
    json.dump({"segments": txt}, open(os.path.join(ROOT, "out", "transcripts", "folge16_dhulkifl_ton.json"), "w"), ensure_ascii=False, indent=1)
    print("duration", subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)

def imgcheck():
    import folgen10_14 as m
    m.IMG.update(json.load(open(os.path.join(ROOT, "assets", "img_registry_15_25.json"))))
    od = os.path.join(ROOT, "out", "folge16_dhulkifl_imgcheck"); os.makedirs(od, exist_ok=True)
    for n in sorted(set(p[1] for p in S["plan"])):
        f = f"{W}/{n}.img"
        req = urllib.request.Request(m.B + m.IMG[n], headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
        open(f, "wb").write(urllib.request.urlopen(req, timeout=120).read())
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", f, "-vf", "scale=960:-1", "-q:v", "4", f"{od}/{n}_full.jpg")
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", f, "-filter_complex",
           "[0]split=4[a][b][c][d];[a]crop=iw/2:ih/2:0:0[q1];[b]crop=iw/2:ih/2:iw/2:0[q2];[c]crop=iw/2:ih/2:0:ih/2[q3];[d]crop=iw/2:ih/2:iw/2:ih/2[q4];[q1][q2][q3][q4]xstack=inputs=4:layout=0_0|w0+8_0|0_h0+8|w0+8_h0+8:fill=white,scale=1280:-1",
           "-q:v", "4", f"{od}/{n}_quarters.jpg")
        print("ok", n)

if __name__ == "__main__":
    {"narration": narration, "imgcheck": imgcheck}[sys.argv[1]]()
