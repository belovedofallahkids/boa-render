import json,subprocess,sys,math
D=sys.argv[1]; J=json.load(open(sys.argv[2])); AMB=float(sys.argv[3]) if len(sys.argv)>3 else -26
segs=J['segments']; T=J['duration']
place=json.load(open(f'{D}/place.json'))
words=[(float(a),float(b),w) for a,b,w in (l.split(None,2) for l in open(f'{D}/track_tr.txt') if l.strip())]
dur={l.split()[0]:float(l.split()[1]) for l in open(f'{D}/durs.txt')}
bed={'s1a':'night_room','s1b':'night_room','s1c':'night_room','s2a':'desert_camp','s2b':'night_room','s2c':'lamp_dawn','s3a':'lamp_dawn','s3b':'dream_sky','s3c':'night_room','s3d':'dream_sky','s4a':'evening_wind','s4b':'night_room','s4c':'evening_wind','s4d':'evening_wind','s5a':'soft_rain','s5b':'lamp_dawn','s5c':'night_room','s5d':'desert_camp','s6a':'lamp_dawn','s6b':'night_room','s6c':'lamp_dawn','s7a':'night_room','s7b':'night_room'}
run=lambda c: subprocess.run(c,check=True,capture_output=True)
ids=[s['id'] for s in segs]
pieces=[]; report=[]
for i,s in enumerate(segs):
    k=s['id']; st=s['start']; en=segs[i+1]['start'] if i+1<len(segs) else T-6.0  # keep 6s calm tail at the very end
    p0=place[k]; nxt=place[ids[i+1]] if i+1<len(ids) else 1e9
    P=json.load(open(f'{D}/pauses.json'))[k]
    SP=[x for x in json.load(open(f'{D}/ayah_spans.json')).get(k,[]) if x]
    gaps=[(c,d) for c,d in P if d>=0.5 and 1.2<c<dur[k]-1.2 and not any(a<=c<=b for a,b in SP)]
    lead=0.6 if k=='s1a' else 0.35
    F=(en-st)-lead-dur[k]-0.8
    n=min(len(gaps), max(0,int(F//2.2)), 5)
    cuts=sorted(c for c,_ in sorted(gaps,key=lambda x:-x[1])[:n])
    g=min(2.2, F/(n+1)) if n else 0
    t=st+lead; prev=0.0
    for c in cuts+[dur[k]]:
        pieces.append((k,prev,c,t)); t+=c-prev+g; prev=c
    report.append(f"{k}:{n}x{g:.1f}s")
inputs=[];flt=[];idx=0
# ambient runs
runs=[]
for i,s in enumerate(segs):
    en=segs[i+1]['start'] if i+1<len(segs) else T
    if runs and runs[-1][0]==bed[s['id']]: runs[-1][2]=en
    else: runs.append([bed[s['id']],s['start'],en])
for b in set(bed.values()):
    run(['ffmpeg','-y','-i',f'{D}/amb/{b}.mp3','-af',f'loudnorm=I={AMB}:TP=-9:LRA=7','-ar','48000','-ac','2',f'{D}/amb/{b}_n2.wav'])
for k2,(b,st,en) in enumerate(runs):
    L=en-st+1.0; p=f'{D}/run2_{k2}.wav'
    run(['ffmpeg','-y','-stream_loop','-1','-i',f'{D}/amb/{b}_n2.wav','-t',f'{L:.3f}','-af',f'afade=t=in:d=1,afade=t=out:st={L-1:.3f}:d=1',p])
    inputs+=['-i',p]; flt.append(f'[{idx}]adelay={int(st*1000)}|{int(st*1000)}[b{idx}]'); idx+=1
nb=idx
for (k,a,b,t) in pieces:
    inputs+=['-i',f'{D}/{k}.mp3']
    flt.append(f'[{idx}]aresample=48000,aformat=channel_layouts=stereo,atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={max(0,b-a-0.05):.3f}:d=0.05,adelay={int(t*1000)}|{int(t*1000)}[v{idx}]'); idx+=1
flt.append(''.join(f'[b{i}]' for i in range(nb))+f'amix=inputs={nb}:normalize=0,atrim=0:{T}[amb]')
flt.append(''.join(f'[v{i}]' for i in range(nb,idx))+f'amix=inputs={idx-nb}:normalize=0,apad=whole_dur={T},atrim=0:{T},asplit[voice][key]')
flt.append('[amb][key]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=600[ambd]')
flt.append(f'[voice][ambd]amix=inputs=2:normalize=0,afade=t=out:st={T-1}:d=1[m]')
run(['ffmpeg','-y',*inputs,'-filter_complex',';'.join(flt),'-map','[m]','-ar','48000',f'{D}/mix2_raw.wav'])
print(' '.join(report))
