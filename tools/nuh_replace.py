#!/usr/bin/env python3
"""Folge 03 Nuh – replacement file (H16, H47). Free.
1) original video = Descript composition 6e75bc7e (unchanged since 01.10.2026)
2) align its sound with Orshot audio 260 (where the cut was tested)
3) remove only the wrong word 'nicht' (Hud 43): 260-time 232.90-233.30 (tested: '...der schützt vor dem Wasser.')
4) end: 5 s still of last frame + 1 s fade (rule), loudness -14 LUFS
5) checks: word transcript of the FINAL file, silencedetect, blackdetect, loudness, one frame per 10 s
"""
import json, os, subprocess, sys, urllib.request
import numpy as np
OUT = "out/nuh_fix/replace"; os.makedirs(OUT, exist_ok=True)
VID = sys.argv[1]
A260 = "https://storage.orshot.com/cloud/w-12325/renders/audio/boa_folge03_nuh_alt_ton_mit_schrittenm4a-K5ddGJhffjV.m4a"
def get(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
    with urllib.request.urlopen(req, timeout=600) as r, open(path, "wb") as f:
        f.write(r.read())
def run(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)
get(VID, "/tmp/orig.mp4"); get(A260, "/tmp/a260.m4a")
probe = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", "/tmp/orig.mp4").stdout)
rep = {"orig_probe": {"duration": probe["format"]["duration"],
                      "streams": [{k: s.get(k) for k in ("codec_type", "codec_name", "width", "height", "r_frame_rate", "sample_rate")} for s in probe["streams"]]}}
sr = 16000
def pcm(p):
    return np.frombuffer(run("ffmpeg", "-loglevel", "error", "-i", p, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-").stdout.encode("latin1") if False else
                         subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
xo, x6 = pcm("/tmp/orig.mp4"), pcm("/tmp/a260.m4a")
# offset: correlate envelopes (10 ms) of 200-260 s
def envl(x, t0, t1):
    a = x[int(t0 * sr):int(t1 * sr)]; n = len(a) // 160
    return np.log(np.abs(a[:n * 160]).reshape(n, 160).max(1) + 1e-3)
e6 = envl(x6, 200, 260)
best = max((np.corrcoef(envl(xo, 200 + l / 100, 260 + l / 100)[:len(e6)], e6)[0, 1], l / 100) for l in range(-300, 301))
rep["offset_orig_minus_260"] = best[1]; rep["offset_corr"] = round(float(best[0]), 4)
c0, c1 = 232.90 + best[1], 233.30 + best[1]          # cut in original-video time
rep["cut_in_orig"] = [round(c0, 3), round(c1, 3)]
dur = float(probe["format"]["duration"])
# build: video [0,c0] + [c1,end] ; then tail 5 s of last frame + 1 s fade ; audio with 15 ms fades at the joint
fc = (f"[0:v]trim=0:{c0},setpts=PTS-STARTPTS[v1];[0:v]trim={c1},setpts=PTS-STARTPTS[v2];"
      f"[0:a]atrim=0:{c0},asetpts=PTS-STARTPTS,afade=t=out:st={c0-0.015}:d=0.015[a1];"
      f"[0:a]atrim={c1},asetpts=PTS-STARTPTS,afade=t=in:d=0.015[a2];"
      f"[v1][a1][v2][a2]concat=n=2:v=1:a=1[v][a];"
      f"[v]tpad=stop_mode=clone:stop_duration=5,fade=t=out:st={dur-(c1-c0)+4}:d=1,format=yuv420p[vo];"
      f"[a]apad=pad_dur=5,loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
r = run("ffmpeg", "-y", "-loglevel", "error", "-i", "/tmp/orig.mp4", "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", f"{OUT}/folge03_nuh_v2.mp4")
rep["ffmpeg_err"] = r.stderr[-1500:]
F = f"{OUT}/folge03_nuh_v2.mp4"
rep["final_duration"] = run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", F).stdout.strip()
lo = run("ffmpeg", "-i", F, "-af", "ebur128", "-f", "null", "-").stderr
rep["loudness"] = [l.strip() for l in lo.splitlines()[-12:] if "I:" in l or "LRA:" in l or "Peak" in l]
rep["silences_over_2.5s"] = [l.split("] ")[1] for l in run("ffmpeg", "-i", F, "-af", "silencedetect=n=-45dB:d=2.5", "-f", "null", "-").stderr.splitlines() if "silence_" in l]
rep["black"] = [l.split("] ")[1] for l in run("ffmpeg", "-i", F, "-vf", "blackdetect=d=0.3:pix_th=0.1", "-an", "-f", "null", "-").stderr.splitlines() if "black_start" in l]
os.makedirs(f"{OUT}/frames", exist_ok=True)
run("ffmpeg", "-y", "-loglevel", "error", "-i", F, "-vf", "fps=1/10,scale=480:-1", f"{OUT}/frames/f_%03d.jpg")
run("ffmpeg", "-y", "-loglevel", "error", "-i", F, "-vf", "fps=1/10,scale=320:-1,tile=6x6", "-frames:v", "1", f"{OUT}/contact.jpg")
run("ffmpeg", "-y", "-loglevel", "error", "-ss", str(c0 - 4), "-i", F, "-t", "8", "-vn", "-c:a", "libmp3lame", "-q:a", "3", f"{OUT}/joint_check.mp3")
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
segs, _ = m.transcribe(F, language="de", word_timestamps=True, vad_filter=False)
lines, txt = [], []
for s in segs:
    txt.append(f"{s.start:7.2f} {s.text.strip()}")
    lines += [f"{w.start:8.3f} {w.end:8.3f} {w.word.strip()}" for w in (s.words or [])]
open(f"{OUT}/final_transcript.txt", "w").write("\n".join(txt) + "\n")
open(f"{OUT}/final_words.txt", "w").write("\n".join(lines) + "\n")
rep["joint_text"] = [t for t in txt if 220 < float(t.split()[0]) < 240]
json.dump(rep, open(f"{OUT}/report.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=1))
