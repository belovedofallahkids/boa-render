#!/usr/bin/env python3
"""Harun 15 DE v2: splice 8 corrected Oma lines (dub/folge15_harun_de_v2_units.json) into v1 audio. Run in a dir with orig.wav, d01..d08.mp3."""
import json,subprocess,numpy as np,soundfile as sf
def sh(*a): subprocess.run(list(a),check=True)
def lufs(f):
    r=subprocess.run(["ffmpeg","-i",f,"-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    return float(r.split("Integrated loudness:")[1].split("I:")[1].split("LUFS")[0])
x,sr=sf.read("orig.wav"); N=len(x); out=x.copy()
def prep(src,ref):
    sh("ffmpeg","-y","-loglevel","error","-ss",str(ref[0]),"-to",str(ref[1]),"-i","orig.wav","ref.wav")
    L=lufs("ref.wav")
    sh("ffmpeg","-y","-loglevel","error","-i",src,"-af",f"silenceremove=start_periods=1:start_threshold=-45dB,loudnorm=I={L}:TP=-1.5:LRA=7","-ar",str(sr),"-ac","2","p.wav")
    y,_=sf.read("p.wav"); a=np.abs(y).max(1); idx=np.where(a>0.01)[0]; return y[:idx[-1]+int(0.12*sr)]
def orig(a,b): return x[int(a*sr):int(b*sr)].copy()
for a,b in [(49.9,54.2),(146.6,164.3),(242.3,249.3),(253.95,299.3)]: out[int(a*sr):int(b*sr)]=0
log=[]
def put(y,t,name):
    n=len(y); f=int(0.02*sr); y[:f]*=np.linspace(0,1,f)[:,None]; y[-f:]*=np.linspace(1,0,f)[:,None]
    i=int(t*sr); out[i:i+n]+=y; e=t+n/sr; log.append((name,round(t,2),round(e,2))); return e
put(prep("d01.mp3",(43,49)),50.1,"d01")
e=put(prep("d02.mp3",(137,146)),146.8,"d02")
e=put(prep("d03.mp3",(137,146)),max(154.0,e+0.7),"d03"); assert e<164.3,e
e=put(prep("d04.mp3",(233.5,241.4)),242.5,"d04"); assert e<249.3,e
t=254.0
e=put(prep("d05.mp3",(233.5,241.4)),t,"d05")
e=put(orig(260.75,264.35),e+0.8,"orig Sohn meiner Mutter")
e=put(prep("d06.mp3",(261,264.3)),e+0.8,"d06")
e=put(prep("d07.mp3",(261,264.3)),e+0.8,"d07")
e=put(prep("d08.mp3",(289,298)),max(e+1.0,274.6),"d08")
e=put(orig(289.0,298.45),e+0.6,"orig Barmherzigkeit…Barmherzigen"); assert e<299.4,e
sf.write("de_v2.wav",np.clip(out,-1,1),sr)
for l in log: print(l)
