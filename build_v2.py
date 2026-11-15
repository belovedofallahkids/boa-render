#!/usr/bin/env python3
"""Short Musa «Das Meer teilt sich» v2: image change every ~3-7 s by narrative beat; en/fr re-voiced
with local prophet names (Moses/Moïse, tools/short_tts.py); de/ar = published audio 453.8–509.4."""
import json, re, subprocess, sys, os
S = '/home/claude/src'; R = '/home/claude/boa-render'
VID = f'{S}/musa.mp4'; T0 = 453.8
def sh(*a): subprocess.run(a, check=True)
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
def silences(f, ss=0, t=None):
    a = ['ffmpeg','-ss',str(ss)] + (['-t',str(t)] if t else []) + ['-i',f,'-vn','-af','silencedetect=n=-35dB:d=0.25','-f','null','-']
    o = subprocess.run(a, capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
    return [((a_+b_)/2) for a_, b_ in zip(st, en)]
def snap(t, sil, tol=1.2):
    c = min(sil, key=lambda s: abs(s-t), default=t)
    return c if abs(c-t) <= tol else t

TXT = {
 'de': ("Musa sagte: Keineswegs! Denn mit mir ist mein Herr; Er wird mich leiten. Da gab Allah Musa ein: Schlag mit deinem Stock auf das Meer! Da spaltete es sich, und jeder Teil war wie ein gewaltiger Berg. Und dazwischen war ein trockener Weg durch das Meer!",
        "Musa und die Kinder Israils gingen sicher hindurch. Als Pharao mit seinem Heer folgte, schloss sich das Meer wieder. Allah hatte Musa und alle, die bei ihm waren, gerettet.",
        ["Da gab Allah", "Da spaltete", "Und dazwischen"], ["Als Pharao", "Allah hatte"])}
for L in ['en','fr','ar']:
    d = json.load(open(f'{R}/dub/folge14_musa_{L}_from_ar_v1.json'))
    TXT[L] = (d['s6c'], d['s6d'],
      {'en':["Then We inspired","and it parted","And in the middle"],'fr':["Alors Nous","Elle se fendit","Et au milieu"],'ar':["﴿فَأَوْحَيْنَا","فَانْفَلَقَ","وصار في وسط"]}[L],
      {'en':["And when Pharaoh","“And We saved"],'fr':["Et quand Pharaon","« Et Nous sauv"],'ar':["ولما تبعهم","﴿وَأَنْجَيْنَا"]}[L])

def beat_times(text, marks, a, b, sil):
    out = []
    for m in marks:
        i = text.find(m); assert i >= 0, m
        out.append(snap(a + (b-a)*i/len(text), sil))
    return out

def audio_and_beats(L, od):
    if L in ('de','ar'):
        src = VID if L == 'de' else f'{S}/media-dub-musa-v10/folge14_musa_ar_v10.mp3'
        sh('ffmpeg','-v','error','-y','-ss',str(T0),'-t','55.6','-i',src,'-vn','-ac','2','-ar','48000',f'{od}/a_{L}.wav')
        sil = silences(f'{od}/a_{L}.wav')
        t_c, t_e, total = 457.297-T0, 503.861-T0, 55.6
        # end of s6d speech = last silence before s6e image
        end_d = max([s for s in sil if s < t_e+0.3] or [t_e])
        c, d_, mc, md = TXT[L]
        full = c + ' ' + d_
        tc = t_c + 0.35
        b = beat_times(full, mc + [d_[:12]] + md, tc, end_d, sil)
        return f'{od}/a_{L}.wav', [0, t_c, tc] and [0, t_c] + b[:3] + [b[3]] + b[4:] + [t_e], total
    # en/fr: assemble new TTS lines
    tts = f'{S}/tts'; parts = []; t = 0.0; starts = {}
    for k, gap in [('s6b',0.5),('s6c',0.6),('s6d',0.6),('s6e',0.8)]:
        f = f'{tts}/{L}_{k}.mp3'; starts[k] = t; parts.append((f, gap)); t += dur(f) + gap
    total = t + 0.4
    inp = []; fc = ''
    for i, (f, g) in enumerate(parts):
        inp += ['-i', f]; fc += f'[{i}:a]aresample=48000,apad=pad_dur={g}[p{i}];'
    fc += ''.join(f'[p{i}]' for i in range(len(parts))) + f'concat=n={len(parts)}:v=0:a=1,apad=pad_dur=0.4[o]'
    sh('ffmpeg','-v','error','-y',*inp,'-filter_complex',fc,'-map','[o]','-ac','2',f'{od}/a_{L}.wav')
    c, d_, mc, md = TXT[L]
    sc = silences(f'{tts}/{L}_s6c.mp3'); sd = silences(f'{tts}/{L}_s6d.mp3')
    bc = [starts['s6c'] + x for x in beat_times(c, mc, 0, dur(f'{tts}/{L}_s6c.mp3'), sc)]
    bd = [starts['s6d'] + x for x in beat_times(d_, md, 0, dur(f'{tts}/{L}_s6d.mp3'), sd)]
    cut = lambda k: max(0, starts[k] - 0.3)
    return f'{od}/a_{L}.wav', [0, cut('s6c')] + bc + [cut('s6d')] + bd + [cut('s6e')], total

# shots: (kind, source, motion)
SHOTS = [('vid', 454.5, ('fix', 560)),                                   # Ilyas asks
         ('img', f'{R}/assets/h59/folge14/h59_musa_sea_dust_horizon.jpg', 'pan_r'),   # trust: "my Lord is with me"
         ('img', f'{R}/out/sheets/folge14_bilder_1_big/07_staff_glow.jpg', 'zoom'),   # strike with your staff
         ('vid', 470.0, ('zoomc', 656)),                                 # it parted, like mountains
         ('vid', 480.0, ('pan', 0, 1312)),                               # dry path
         ('vid', 490.0, ('pan', 1312, 300)),                             # crossed safely
         ('img', f'{R}/assets/h59/folge14/h59_musa_sea_calm_whole.jpg', 'zoom_out'),  # sea closed
         ('img', f'{R}/assets/h59/folge14/h59_musa_sea_golden_beam.jpg', 'zoom'),     # We saved Musa
         ('vid', 504.6, ('fix', 776))]                                   # Noah: the sea split!

def shot(i, s, d, od):
    o = f'{od}/shot{i}.mp4'; kind, src, mo = s
    enc = ['-r','30','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-an']
    if kind == 'vid':
        if mo[0] == 'fix': vf = f"crop=608:1080:{mo[1]}:0,scale=1080:1920:flags=lanczos"
        elif mo[0] == 'pan': vf = f"crop=608:1080:x='{mo[1]}+({mo[2]}-{mo[1]})*t/{d}':y=0,scale=1080:1920:flags=lanczos"
        else: vf = f"crop=608:1080:{mo[1]}:0,scale=w=-2:h='1920*(1+0.12*t/{d})':eval=frame:flags=lanczos,crop=1080:1920"
        sh('ffmpeg','-v','error','-y','-ss',str(src),'-t',f'{d:.3f}','-i',VID,'-vf',vf+',setsar=1',*enc,'-t',f'{d:.3f}',o)
    else:
        # still 16:9 -> scale to height 2200, 9:16 window with gentle motion
        base = "scale=-2:2200,"
        if mo == 'pan_r': cr = f"crop=1238:2200:x='(in_w-1238)*0.15+(in_w-1238)*0.7*t/{d}':y=0"
        elif mo == 'zoom': cr = f"crop=1238:2200,scale=w=-2:h='1920*(1+0.15*t/{d})':eval=frame:flags=lanczos,crop=1080:1920"
        else: cr = f"crop=1238:2200,scale=w=-2:h='1920*(1.15-0.15*t/{d})':eval=frame:flags=lanczos,crop=1080:1920"
        sh('ffmpeg','-v','error','-y','-loop','1','-framerate','30','-t',f'{d:.3f}','-i',src,'-vf',base+cr+',scale=1080:1920:flags=lanczos,setsar=1',*enc,'-t',f'{d:.3f}',o)
    return o

def build(L):
    od = f'/home/claude/v2/w_{L}'; os.makedirs(od, exist_ok=True)
    a, cuts, total = audio_and_beats(L, od)
    cuts = cuts + [total]
    assert len(cuts) == len(SHOTS) + 1, (L, cuts)
    # frame-exact durations
    fr = [round(c*30) for c in cuts]
    clips = [shot(i, s, (fr[i+1]-fr[i])/30, od) for i, s in enumerate(SHOTS)]
    print(L, [round(c,2) for c in cuts], flush=True)
    open(f'{od}/list.txt','w').write(''.join(f"file '{c}'\n" for c in clips))
    sh('ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{od}/list.txt','-c','copy',f'{od}/v.mp4')
    T = fr[-1]/30
    sh('ffmpeg','-v','error','-y','-i',f'{od}/v.mp4','-i',a,'-loop','1','-t',f'{T:.3f}','-i',f'/home/claude/v2/ov_{L}.png',
       '-filter_complex', f"[0:v][2:v]overlay=0:0:format=auto,fade=t=in:st=0:d=0.3,fade=t=out:st={T-0.5:.3f}:d=0.5,format=yuv420p[vo];"
       f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={T-0.5:.3f}:d=0.5,aresample=48000[ao]",
       '-map','[vo]','-map','[ao]','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-b:a','192k',
       '-movflags','+faststart','-t',f'{T:.3f}',f'/home/claude/v2/out/Short_Musa_Meer_v2_{L}.mp4')
    json.dump({'cuts': cuts}, open(f'/home/claude/v2/out/cuts_{L}.json','w'))

if __name__ == '__main__':
    os.makedirs('/home/claude/v2/out', exist_ok=True)
    for L in sys.argv[1:]: build(L)
