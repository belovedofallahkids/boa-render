# voice-only dub track: sentences start with their image, long sentences split at natural pauses (never inside a verse),
# optional extra lines: OPEN (before s1a) and CLOSE (inside s7b before the goodnight)
import json,subprocess,sys
D=sys.argv[1]; J=json.load(open(sys.argv[2])); out=sys.argv[3]
segs=J['segments']; T=J['duration']
dur={l.split()[0]:float(l.split()[1]) for l in open(f'{D}/durs.txt')}
P=json.load(open(f'{D}/pauses.json')); SPAN=json.load(open(f'{D}/ayah_spans.json'))
probe=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
import os
OPEN=f'{D}/open.mp3' if os.path.exists(f'{D}/open.mp3') else None
CLOSE=f'{D}/close.mp3' if os.path.exists(f'{D}/close.mp3') else None
GMAX=2.4
pieces=[]; rep=[]; resid=[]
SHARE={'s4c':'s4d'}; carry=None
for i,s in enumerate(segs):
    k=s['id']; st=s['start']; en=segs[i+1]['start'] if i+1<len(segs) else T-1.5
    t=st+(0.3 if k=='s1a' else 0.35)
    if carry is not None: t=carry+1.0; carry=None
    if k in SHARE:
        nk=SHARE[k]; j2=[x['id'] for x in segs].index(nk); en2=segs[j2+1]['start']
        xn=f'{D}/x_{nk}.mp3'; need=dur[nk]+1.0+(probe(xn)+1.0 if os.path.exists(xn) else 0)+0.4
        en=en2-need
    if k=='s1a' and OPEN:
        od=probe(OPEN); pieces.append((OPEN,0,od,t)); t+=od+0.8
    XA=f'{D}/x_{k}.mp3' if os.path.exists(f'{D}/x_{k}.mp3') else None
    xa=probe(XA) if XA else 0
    sp=[x for x in SPAN.get(k,[]) if x]
    extra=[]
    if k=='s7b' and CLOSE:
        cd=probe(CLOSE); extra=[(16.23,cd)]
    used=sum(d for _,d in extra)+0.9*len(extra)+(xa+1.0 if XA else 0)
    F=(en-t)-dur[k]-used-0.4
    cands=[(c,d) for c,d in P[k] if d>=0.4 and 1.2<c<dur[k]-1.2 and not any(a<=c<=b for a,b in sp) and all(abs(c-x)>0.5 for x,_ in extra)]
    n=min(len(cands), max(0,int(F//1.6)), 7)
    cuts=sorted(c for c,_ in sorted(cands,key=lambda x:-x[1])[:n])
    g=min(GMAX, F/(n+1)) if n else 0
    allc=sorted(set(cuts+[x for x,_ in extra]))
    prev=0.0
    for c in allc+[dur[k]]:
        pieces.append((f'{D}/{k}.mp3',prev,c,t)); t+=c-prev
        if c in [x for x,_ in extra]:
            cd=dict(extra)[c]; t+=0.9; pieces.append((CLOSE,0,cd,t)); t+=cd+0.9
        elif c!=dur[k]: t+=g
        prev=c
    if XA:
        t+=1.0; pieces.append((XA,0,xa,t)); t+=xa
    if k in SHARE: carry=t
    resid.append(round(en-t,1)); rep.append(f'{k}:{n}x{g:.1f}')
inputs=[];flt=[]
for j,(f,a,b,t) in enumerate(pieces):
    inputs+=['-i',f]
    flt.append(f'[{j}]aresample=48000,aformat=channel_layouts=stereo,atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(0,b-a-0.04):.3f}:d=0.04,adelay={int(t*1000)}|{int(t*1000)}[v{j}]')
flt.append(''.join(f'[v{j}]' for j in range(len(pieces)))+f'amix=inputs={len(pieces)}:normalize=0,apad=whole_dur={T},atrim=0:{T},afade=t=out:st={T-1}:d=1[m]')
subprocess.run(['ffmpeg','-y',*inputs,'-filter_complex',';'.join(flt),'-map','[m]','-ar','48000',out],check=True,capture_output=True)
print(' '.join(rep)); print('end-of-scene silence per sentence:',dict(zip([s['id'] for s in segs],resid)))
