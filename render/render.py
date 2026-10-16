#!/usr/bin/env python3
"""BoA render: jobs/*.json -> MP4 1920x1080 30fps, narration normalised to -14 LUFS.

The finished video and a check sheet are published as a GitHub release
(public URL); out/<name>/status.json, contact.jpg and log.txt are committed
back so the result can be checked without opening the video.

Job file (jobs/<name>.json):
{
  "name": "folge07_lut_v1",
  "audio": "https://.../narration.mp3",
  "audio_start": 0, "audio_end": 480.5,          # optional trim (seconds)
  "crossfade": 0.6, "fade_in": 0.5, "fade_out": 1.5, "loudness": -14,
  "tail_hold": 6,                                 # optional: silence after the last word, last picture stays
  "segments": [
    {"image": "https://...", "start": 0, "end": 7.2, "motion": "zoom_in"},
    {"image": "https://...", "start": 7.2, "end": 12, "motion": "pan_right",
     "crop": [0.0, 0.0, 0.7]}                     # optional [x, y, w] fractions, 16:9 kept
  ]
}
motion: zoom_in | zoom_out | pan_left | pan_right | pan_up | pan_down | none
Segments must be back to back (start == previous end).
"""
import concurrent.futures as cf
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import time
import traceback
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "belovedofallahkids/boa-render")
WORK = os.path.join(ROOT, "work")
CACHE = os.path.join(WORK, "cache")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1920, 1080
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def run(cmd):
    log("+", " ".join(cmd)[:400])
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        log((p.stderr or "")[-3000:])
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)[:200]}")
    return (p.stdout or "") + (p.stderr or "")


def fetch(url):
    ext = os.path.splitext(url.split("?")[0])[1][:6] or ".bin"
    dest = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ext)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (boa-render)"})
            with urllib.request.urlopen(req, timeout=180) as r, open(dest + ".part", "wb") as f:
                shutil.copyfileobj(r, f)
            os.replace(dest + ".part", dest)
            if os.path.getsize(dest) > 0:
                return dest
        except Exception as e:  # noqa: BLE001
            last = e
            log("download retry", attempt + 1, url[:120], repr(e))
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"download failed: {url} ({last!r})")


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out.strip().splitlines()[0])


def motion_expr(motion, frames, amount):
    a = amount
    p = f"(on/{max(frames - 1, 1)})"
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if motion == "zoom_out":
        return f"{1 + a}-{a}*{p}", cx, cy
    if motion == "pan_left":
        return f"{1 + a}", f"(iw-iw/zoom)*(1-{p})", cy
    if motion == "pan_right":
        return f"{1 + a}", f"(iw-iw/zoom)*{p}", cy
    if motion == "pan_up":
        return f"{1 + a}", cx, f"(ih-ih/zoom)*(1-{p})"
    if motion == "pan_down":
        return f"{1 + a}", cx, f"(ih-ih/zoom)*{p}"
    if motion == "none":
        return "1", "0", "0"
    return f"1+{a}*{p}", cx, cy  # zoom_in (default)


def render_clip(i, seg, img, length, fps, out):
    frames = int(round(length * fps)) + 2  # small pad, the crossfade drops the excess
    z, x, y = motion_expr(seg.get("motion", "zoom_in"), frames, float(seg.get("amount", 0.08)))
    vf = []
    if seg.get("crop"):
        cx, cy, cw = seg["crop"]
        vf.append(f"crop=w='iw*{cw}':h='iw*{cw}*9/16':x='iw*{cx}':y='ih*{cy}'")
    vf.append("scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,crop=3840:2160")
    vf.append(f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={fps}")
    vf.append("format=yuv420p")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", img, "-vf", ",".join(vf),
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
         "-x264-params", "threads=2", "-pix_fmt", "yuv420p", "-r", str(fps), out])
    return i


def cut_audio(src, cuts, out_wav):
    """Remove [start, end] ranges (seconds, source time) with 15 ms fades at every joint."""
    total = duration(src)
    keep, pos = [], 0.0
    for a, b in sorted(cuts):
        if a > pos:
            keep.append((pos, a))
        pos = max(pos, b)
    if pos < total:
        keep.append((pos, total))
    fc, labels = [], []
    for i, (a, b) in enumerate(keep):
        d = b - a
        fc.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.015,afade=t=out:st={max(d - 0.015, 0):.3f}:d=0.015[p{i}]")
        labels.append(f"[p{i}]")
    fc.append(f"{''.join(labels)}concat=n={len(keep)}:v=0:a=1[out]")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-filter_complex", ";".join(fc),
         "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", out_wav])
    log(f"audio cuts: {len(cuts)} removed, {len(keep)} parts kept, {duration(out_wav):.2f}s left")
    return out_wav


def normalise_audio(job, out_wav):
    src = fetch(job["audio"])
    if job.get("audio_cuts"):
        src = cut_audio(src, job["audio_cuts"], out_wav + ".cut.wav")
    trim = []
    if job.get("audio_start") is not None:
        trim += ["-ss", str(job["audio_start"])]
    if job.get("audio_end") is not None:
        trim += ["-to", str(job["audio_end"])]
    target = float(job.get("loudness", -14))
    base = f"loudnorm=I={target}:TP=-1.5:LRA=11"
    txt = run(["ffmpeg", "-hide_banner", "-nostats", *trim, "-i", src, "-af",
               base + ":print_format=json", "-f", "null", "-"])
    m = json.loads(txt[txt.rfind("{"): txt.rfind("}") + 1])
    second = (f"{base}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
              f":offset={m['target_offset']}:linear=true:print_format=summary")
    run(["ffmpeg", "-hide_banner", "-nostats", "-y", *trim, "-i", src, "-af", second,
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out_wav])
    return {"input_lufs": float(m["input_i"])}


def check_loudness(path):
    txt = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a",
               "-af", "ebur128=peak=true", "-f", "null", "-"])
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(i[-1]) if i else None), (float(p[-1]) if p else None)


def contact_sheet(video, segs, outdir):
    tdir = os.path.join(outdir, "thumbs")
    os.makedirs(tdir, exist_ok=True)
    cols = 6
    rows = math.ceil(len(segs) / cols)
    font = f"fontfile={FONT}:" if os.path.exists(FONT) else ""
    for k in range(rows * cols):
        dest = os.path.join(tdir, f"{k:03d}.jpg")
        if k < len(segs):
            s = segs[k]
            t = (s["start"] + s["end"]) / 2
            label = f"{k + 1}  {int(s['start'] // 60)}m{s['start'] % 60:04.1f}s  {s.get('label', '')}"
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", video,
                 "-frames:v", "1", "-vf",
                 f"scale=480:270,drawtext={font}text='{label}':x=8:y=8:fontsize=24:"
                 f"fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=4", "-q:v", "4", dest])
        else:
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                 "color=c=black:s=480x270", "-frames:v", "1", dest])
    sheet = os.path.join(outdir, "contact.jpg")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "1", "-i",
         os.path.join(tdir, "%03d.jpg"), "-vf", f"tile={cols}x{rows}:padding=4:color=black",
         "-frames:v", "1", "-q:v", "4", sheet])
    shutil.rmtree(tdir, ignore_errors=True)
    return sheet


def publish(name, files):
    tag = name
    exists = subprocess.run(["gh", "release", "view", tag, "--repo", REPO],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    if exists:
        run(["gh", "release", "upload", tag, *files, "--clobber", "--repo", REPO])
    else:
        run(["gh", "release", "create", tag, *files, "--repo", REPO, "--title", name,
             "--notes", "BoA render (automatisch). Erst nach 2 Pruefungen und Freigabe hochladen."])
    return {os.path.basename(f): f"https://github.com/{REPO}/releases/download/{tag}/{os.path.basename(f)}"
            for f in files}


def render_job(job, job_hash, outdir):
    name = job["name"]
    fps = int(job.get("fps", 30))
    xf = float(job.get("crossfade", 0.6))
    segs = [dict(s) for s in job["segments"]]
    jdir = os.path.join(WORK, name)
    os.makedirs(jdir, exist_ok=True)

    t0 = time.time()
    audio = os.path.join(jdir, "audio.wav")
    aud = normalise_audio(job, audio)
    narration_len = duration(audio)
    tail = float(job.get("tail_hold", 0) or 0)
    if tail > 0:
        # Endbild: Stille nach dem letzten Wort, das letzte Bild bleibt stehen, dann Abblende.
        # So wird das letzte Wort nie von der Abblende ueberdeckt, und der YouTube-Abspann hat Platz.
        padded = os.path.join(jdir, "audio_tail.wav")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", audio,
             "-af", f"apad=pad_dur={tail:.3f}", "-c:a", "pcm_s16le", padded])
        audio = padded
        log(f"tail hold {tail:.1f}s after the narration ({narration_len:.2f}s)")
    audio_len = duration(audio)
    if segs[-1].get("end") in (None, "audio"):
        segs[-1]["end"] = round(audio_len, 3)  # last picture runs to the end of the narration
    for k, s in enumerate(segs):
        if s["end"] - s["start"] <= xf + 0.1:
            raise ValueError(f"segment {k + 1} too short for crossfade")
        if k and abs(s["start"] - segs[k - 1]["end"]) > 0.001:
            raise ValueError(f"segment {k + 1} does not start where segment {k} ends")
    if segs[0]["start"] != 0:
        raise ValueError("first segment must start at 0")
    total = segs[-1]["end"]
    log(f"audio {audio_len:.2f}s, timeline {total:.2f}s")
    if total > audio_len + 0.5:
        raise ValueError(f"pictures ({total:.1f}s) run longer than the narration ({audio_len:.1f}s)")

    imgs = {}
    for s in segs:
        if s["image"] not in imgs:
            imgs[s["image"]] = fetch(s["image"])

    n = len(segs)
    clips = [os.path.join(jdir, f"clip{k:03d}.mp4") for k in range(n)]
    tasks = []
    with cf.ThreadPoolExecutor(max_workers=max(2, (os.cpu_count() or 2))) as ex:
        for k, s in enumerate(segs):
            a = 0 if k == 0 else s["start"] - xf / 2
            b = s["end"] if k == n - 1 else s["end"] + xf / 2
            tasks.append(ex.submit(render_clip, k, s, imgs[s["image"]], b - a, fps, clips[k]))
        for t in cf.as_completed(tasks):
            t.result()
    log(f"clips done in {time.time() - t0:.0f}s")

    inputs = []
    for c in clips:
        inputs += ["-i", c]
    inputs += ["-i", audio]
    fc, prev = [], "[0:v]"
    for k in range(1, n):
        off = segs[k]["start"] - xf / 2
        fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={xf}:offset={off:.3f}[v{k}]")
        prev = f"[v{k}]"
    post = [f"trim=duration={total:.3f}", "setpts=PTS-STARTPTS"]
    if job.get("fade_in"):
        post.append(f"fade=t=in:st=0:d={job['fade_in']}")
    if job.get("fade_out"):
        post.append(f"fade=t=out:st={total - float(job['fade_out']):.3f}:d={job['fade_out']}")
    post.append("format=yuv420p")
    fc.append(f"{prev}{','.join(post)}[vout]")
    video = os.path.join(jdir, f"{name}.mp4")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[vout]", "-map", f"{n}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-movflags", "+faststart", "-t", f"{total:.3f}", video])
    for c in clips:
        os.remove(c)

    lufs, peak = check_loudness(video)
    vlen = duration(video)
    sheet = contact_sheet(video, segs, outdir)
    urls = publish(name, [video, sheet])
    return {
        "name": name, "ok": True, "job_hash": job_hash,
        "video_url": urls[os.path.basename(video)], "contact_url": urls["contact.jpg"],
        "duration_video": round(vlen, 3), "duration_audio": round(audio_len, 3),
        "timeline": round(total, 3), "segments": n,
        "narration_end": round(narration_len, 3), "tail_hold": tail,
        "loudness_lufs": lufs, "true_peak_dbfs": peak, "input_lufs": aud["input_lufs"],
        "size_mb": round(os.path.getsize(video) / 1e6, 1),
        "render_seconds": round(time.time() - t0),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def main():
    os.makedirs(CACHE, exist_ok=True)
    force = os.environ.get("FORCE_JOB", "").strip()
    for jf in sorted(glob.glob(os.path.join(ROOT, "jobs", "*.json"))):
        raw = open(jf, "rb").read()
        job_hash = hashlib.sha1(raw).hexdigest()
        job = json.loads(raw)
        name = job["name"]
        if job.get("disabled"):
            continue
        outdir = os.path.join(ROOT, "out", name)
        st_path = os.path.join(outdir, "status.json")
        if os.path.exists(st_path) and force != name:
            old = json.load(open(st_path))
            if old.get("job_hash") == job_hash and old.get("ok"):
                log("skip (already rendered):", name)
                continue
        os.makedirs(outdir, exist_ok=True)
        LOG.clear()
        log("=== render", name)
        try:
            status = render_job(job, job_hash, outdir)
        except Exception as e:  # noqa: BLE001
            log(traceback.format_exc())
            status = {"name": name, "ok": False, "job_hash": job_hash, "error": repr(e)[:800],
                      "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        json.dump(status, open(st_path, "w"), indent=2, ensure_ascii=False)
        open(os.path.join(outdir, "log.txt"), "w").write("\n".join(LOG[-300:]))
        shutil.rmtree(os.path.join(WORK, name), ignore_errors=True)
        log(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
