#!/usr/bin/env python3
"""Short Ibrahim «Wer hat die Götzen zerbrochen?» (19.11.2026).
Source: published Folge 6 (media-folge06_ibrahim_published, 1280x720), keys s4b..s4h.
de = published German audio 223.16-304.10; ar = Mona lines (dub_ar_folge06_ibrahim_mona);
en/fr = edge-tts with local name Abraham (media-short-tts-ibrahim_goetzen).
Layout 1080x1920: blurred background + 16:9 picture (1080x608) in the middle + title overlay.
Every sentence gets its own camera move (no static picture); s4h uses the idol-square shot
instead of the published 'shh' grandmother image."""
import json, os, subprocess, sys
V = '/home/claude/src/ibrahim_pub.mp4'
W = '/home/claude/short_ib'
KEYS = [('s4b', 223.16, 244.28), ('s4c', 244.28, 254.42), ('s4d', 254.42, 263.54),
        ('s4e', 263.54, 278.28), ('s4f', 278.28, 288.12), ('s4g', 288.12, 290.16),
        ('s4h', 290.16, 304.10)]
# motion: (z0, z1, cx0, cx1, cy0, cy1); source override (time of a still frame) for s4h
MO = {'s4b': (1.00, 1.08, .5, .5, .5, .5), 's4c': (1.00, 1.25, .5, .5, .5, .42),
      's4d': (1.18, 1.18, .30, .70, .55, .55), 's4e': (1.25, 1.00, .5, .5, .45, .5),
      's4f': (1.10, 1.25, .5, .5, .65, .72), 's4g': (1.00, 1.00, .5, .5, .5, .5),
      's4h': (1.00, 1.20, .5, .45, .5, .5)}
STILL = {'s4h': 223.40}
def sh(*a): subprocess.run(a, check=True)
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

def fg_filter(k, D):
    z0, z1, x0, x1, y0, y1 = MO[k]
    z = f"({z0}+({z1}-{z0})*t/{D:.3f})"
    cx = f"({x0}+({x1}-{x0})*t/{D:.3f})"; cy = f"({y0}+({y1}-{y0})*t/{D:.3f})"
    # scale picture to 1080*z wide, then crop a 1080x608 window around (cx,cy)
    return (f"scale=w='trunc(1080*{z}/2)*2':h='trunc(608*{z}/2)*2':eval=frame:flags=lanczos,"
            f"crop=1080:608:x='max(0,min(iw-1080,iw*{cx}-540))':y='max(0,min(ih-608,ih*{cy}-304))'")

def clip(k, vs, ve, D, out):
    """picture for key k, length D (freeze last frame if the key's video range is shorter)."""
    enc = ['-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-an']
    if k in STILL:
        inp = ['-loop', '1', '-framerate', '30', '-t', f'{D:.3f}', '-i', f'{W}/still_{k}.png']
    else:
        inp = ['-ss', f'{vs:.3f}', '-t', f'{ve - vs:.3f}', '-i', V]
    # whole key range is always shown: faster if the sentence is shorter (pictures are calm), freeze if longer
    sp = f"setpts=PTS*{min(1.0, D / (ve - vs)):.4f}," if k not in STILL else ""
    fc = (f"[0:v]{sp}fps=30,tpad=stop_mode=clone:stop_duration={D:.3f},trim=duration={D:.3f},setpts=PTS-STARTPTS,split[a][b];"
          f"[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:2,eq=brightness=-0.18:saturation=1.15[bg];"
          f"[b]{fg_filter(k, D)}[fg];[bg][fg]overlay=0:656,setsar=1[v]")
    sh('ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', fc, '-map', '[v]', *enc, '-t', f'{D:.3f}', out)

def build(L):
    od = f'{W}/w_{L}'; os.makedirs(od, exist_ok=True)
    clips, cuts, t = [], [], 0.0
    if L == 'de':
        sh('ffmpeg', '-v', 'error', '-y', '-ss', '223.16', '-t', f'{304.10 - 223.16:.3f}', '-i', V, '-vn', '-ac', '2', '-ar', '48000',
           '-af', 'apad=pad_dur=0.9', f'{od}/a.wav')
        total = dur(f'{od}/a.wav')
        for i, (k, s, e) in enumerate(KEYS):
            D = (e - s) if i < len(KEYS) - 1 else total - t
            f = f'{od}/{k}.mp4'; clip(k, s, e, D, f); clips.append(f); cuts.append(round(t, 2)); t += D
    else:
        parts = []
        for i, (k, s, e) in enumerate(KEYS):
            src = f'/home/claude/src/ar/{k}.mp3' if L == 'ar' else f'/home/claude/src/tts/{L}_{k}.mp3'
            lead = 0.3 if i == 0 else 0.0
            gap = 0.9 if i == len(KEYS) - 1 else 0.55
            D = lead + dur(src) + gap
            parts.append((src, lead, gap))
            f = f'{od}/{k}.mp4'; clip(k, s, e, D, f); clips.append(f); cuts.append(round(t, 2)); t += D
        inp, fc = [], ''
        for i, (src, lead, gap) in enumerate(parts):
            inp += ['-i', src]
            fc += f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(lead*1000)}|{int(lead*1000)},apad=pad_dur={gap}[p{i}];'
        fc += ''.join(f'[p{i}]' for i in range(len(parts))) + f'concat=n={len(parts)}:v=0:a=1[o]'
        sh('ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', fc, '-map', '[o]', f'{od}/a.wav')
        total = t
    open(f'{od}/list.txt', 'w').write(''.join(f"file '{c}'\n" for c in clips))
    sh('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{od}/list.txt', '-c', 'copy', f'{od}/v.mp4')
    T = min(dur(f'{od}/v.mp4'), dur(f'{od}/a.wav'))
    out = f'{W}/out/Short_Ibrahim_Goetzen_{L}.mp4'
    sh('ffmpeg', '-v', 'error', '-y', '-i', f'{od}/v.mp4', '-i', f'{od}/a.wav', '-loop', '1', '-t', f'{T:.3f}', '-i', f'{W}/ov_{L}.png',
       '-filter_complex', f"[0:v][2:v]overlay=0:0:format=auto,fade=t=in:st=0:d=0.3,fade=t=out:st={T-0.6:.3f}:d=0.6,format=yuv420p[vo];"
       f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={T-0.6:.3f}:d=0.6,aresample=48000[ao]",
       '-map', '[vo]', '-map', '[ao]', '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-c:a', 'aac', '-b:a', '192k',
       '-movflags', '+faststart', '-t', f'{T:.3f}', out)
    json.dump({'cuts': cuts, 'total': round(T, 2)}, open(f'{W}/out/cuts_{L}.json', 'w'))
    print(L, round(T, 2), cuts, flush=True)

if __name__ == '__main__':
    os.makedirs(f'{W}/out', exist_ok=True)
    for k, ts in STILL.items():
        sh('ffmpeg', '-v', 'error', '-y', '-ss', str(ts), '-i', V, '-frames:v', '1', f'{W}/still_{k}.png')
    for L in sys.argv[1:]:
        build(L)
