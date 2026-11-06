import json,subprocess,numpy as np,soundfile as sf
def sh(*a): subprocess.run(list(a),check=True)
def lufs(f):
    r=subprocess.run(["ffmpeg","-i",f,"-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    return float(r.split("Integrated loudness:")[1].split("I:")[1].split("LUFS")[0])
x,sr=sf.read("orig.wav"); N=len(x); out=x.copy()
# d01: compress internal pauses
sh("ffmpeg","-y","-loglevel","error","-i","d01.mp3","-af","silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-40dB,atempo=1.05","-ar",str(sr),"-ac","2","d01c.wav")
mutes=[(0.0,27.38),(119.10,125.0),(161.55,163.75),(312.75,367.40)]
for a,b in mutes: out[int(a*sr):int(b*sr)]=0
P=[("d","d01c.wav",0.05,(0,2.7)),
   ("o",(3.20,24.0),3.75,None),("o",(24.6,27.38),24.6,None),
   ("d","d02.mp3",119.14,(119.14,124.92)),
   ("d","d03.mp3",161.60,(159.78,163.7)),
   ("d","d04.mp3",312.80,(304.2,312.0)),
   ("o",(325.75,367.40),323.25,None)]
log=[]
for kind,src,dst,ref in P:
    if kind=="d":
        sh("ffmpeg","-y","-loglevel","error","-ss",str(ref[0]),"-to",str(ref[1]),"-i","orig.wav","ref.wav")
        L=lufs("ref.wav")
        sh("ffmpeg","-y","-loglevel","error","-i",src,"-af",f"silenceremove=start_periods=1:start_threshold=-45dB,loudnorm=I={L}:TP=-1.5:LRA=7,afade=t=in:d=0.02","-ar",str(sr),"-ac","2","p.wav")
        y,_=sf.read("p.wav")
        # trim trailing silence
        a=np.abs(y).max(1); idx=np.where(a>0.01)[0]; y=y[:idx[-1]+int(0.15*sr)]
    else:
        y=x[int(src[0]*sr):int(src[1]*sr)].copy()
    n=len(y); f=int(0.03*sr); y[:f]*=np.linspace(0,1,f)[:,None]; y[-f:]*=np.linspace(1,0,f)[:,None]
    i=int(dst*sr); out[i:i+n]+=y[:max(0,min(n,N-i))]
    log.append((src if kind=="d" else "orig%s"%(src,), dst, round(dst+n/sr,2)))
sf.write("de_v2.wav",np.clip(out,-1,1),sr)
for l in log: print(l)
