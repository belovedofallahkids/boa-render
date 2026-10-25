import json,subprocess,sys
D=sys.argv[1]; J=json.load(open(sys.argv[2]))
segs=J['segments']; T=J['duration']
bed={'s1a':'night_room','s1b':'night_room','s1c':'night_room','s2a':'desert_camp','s2b':'night_room','s2c':'lamp_dawn',
's3a':'lamp_dawn','s3b':'dream_sky','s3c':'night_room','s3d':'dream_sky','s4a':'evening_wind','s4b':'night_room','s4c':'evening_wind','s4d':'evening_wind',
's5a':'soft_rain','s5b':'lamp_dawn','s5c':'night_room','s5d':'desert_camp','s6a':'lamp_dawn','s6b':'night_room','s6c':'lamp_dawn','s7a':'night_room','s7b':'night_room'}
run=lambda c: subprocess.run(c,check=True,capture_output=True)
# 1) normalise ambient loops to -38 LUFS
for b in set(bed.values()):
    run(['ffmpeg','-y','-i',f'{D}/amb/{b}.mp3','-af','loudnorm=I=-38:TP=-9:LRA=7','-ar','48000','-ac','2',f'{D}/amb/{b}_n.wav'])
# 2) ambient runs
runs=[]
for i,s in enumerate(segs):
    st=s['start']; en=segs[i+1]['start'] if i+1<len(segs) else T
    if runs and runs[-1][0]==bed[s['id']]: runs[-1][2]=en
    else: runs.append([bed[s['id']],st,en])
parts=[]
for k,(b,st,en) in enumerate(runs):
    L=en-st+1.0  # 1s overlap for crossfade
    p=f'{D}/run{k}.wav'
    run(['ffmpeg','-y','-stream_loop','-1','-i',f'{D}/amb/{b}_n.wav','-t',f'{L:.3f}','-af',f'afade=t=in:d=1,afade=t=out:st={L-1:.3f}:d=1',p])
    parts.append((p,st))
# 3) voice placement
inputs=[]; flt=[]; idx=0
for p,st in parts:
    inputs+=['-i',p]; flt.append(f'[{idx}]adelay={int(st*1000)}|{int(st*1000)}[a{idx}]'); idx+=1
place={}
for s in segs:
    st=s['start']+(0.6 if s['id']=='s1a' else 0.35)
    place[s['id']]=st
    inputs+=['-i',f"{D}/{s['id']}.mp3"]
    flt.append(f'[{idx}]aresample=48000,aformat=channel_layouts=stereo,adelay={int(st*1000)}|{int(st*1000)}[a{idx}]'); idx+=1
mix=''.join(f'[a{i}]' for i in range(idx))
flt.append(f'{mix}amix=inputs={idx}:normalize=0:dropout_transition=0,atrim=0:{T},afade=t=out:st={T-1.0}:d=1[m]')
run(['ffmpeg','-y',*inputs,'-filter_complex',';'.join(flt),'-map','[m]','-ar','48000',f'{D}/mix_raw.wav'])
json.dump(place,open(f'{D}/place.json','w'))
print('runs',[(r[0],round(r[1],1),round(r[2],1)) for r in runs])
