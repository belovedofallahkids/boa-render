import json,subprocess,numpy as np,soundfile as sf
def sh(*a): subprocess.run(list(a),check=True)
def lufs(f):
    r=subprocess.run(["ffmpeg","-i",f,"-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    return float(r.split("Integrated loudness:")[1].split("I:")[1].split("LUFS")[0])
x,sr=sf.read("orig.wav"); N=len(x)
out=x.copy()
mutes=[(0.0,17.30),(29.07,39.36),(59.90,68.48),(79.30,85.90),(98.40,113.25),(113.27,127.40),(138.70,141.10),(148.05,150.65),(158.10,182.10),(211.40,214.45),(217.50,227.10),(235.80,238.45),(253.10,289.65),(303.55,305.70)]
# placements: (kind, key_or_src_range, dst, tempo, ref_window for loudness)
P=[("d","d01",0.95,1.0,(0,17.3)),("d","d02",29.12,1.01,(29.07,39.36)),("d","d03",59.96,1.0,(59.9,68.48)),("d","d04",79.36,1.0,(79.3,85.9)),
("d","d05",98.44,1.0,(98.4,113.25)),("d","d06",113.32,1.0,(113.27,122.44)),("o",(122.50,126.10),123.45,1.0,None),
("d","d07",138.76,1.0,(138.7,141.1)),("d","d08",148.10,1.0,(148.05,150.65)),("d","d09",158.15,1.08,(158.45,171.05)),("o",(171.05,175.50),173.0,1.0,None),
("d","d10",177.55,1.06,(176.75,182.1)),("d","d11",211.48,1.0,(211.4,214.45)),("d","d12",217.58,1.0,(217.5,227.1)),("d","d13",235.86,1.0,(235.8,238.45)),
("d","d14",253.15,1.08,(254.4,264.05)),("o",(264.05,284.0),265.05,1.0,None),("d","d15",285.05,1.0,(284.7,289.65)),("d","d16",303.62,1.0,(303.55,305.7))]
for a,b in mutes:
    i,j=int(a*sr),int(b*sr); out[i:j]=0
log=[]
for kind,src,dst,tempo,ref in P:
    if kind=="d":
        sh("ffmpeg","-y","-loglevel","error","-ss",str(ref[0]),"-to",str(ref[1]),"-i","orig.wav","ref.wav")
        L=lufs("ref.wav")
        af=f"atempo={tempo}," if tempo!=1.0 else ""
        sh("ffmpeg","-y","-loglevel","error","-i",f"{src}_t.wav","-af",f"{af}loudnorm=I={L}:TP=-1.5:LRA=7,afade=t=in:d=0.03","-ar",str(sr),"-ac","2","p.wav")
        y,_=sf.read("p.wav")
    else:
        y=x[int(src[0]*sr):int(src[1]*sr)].copy()
    n=len(y); f=int(0.04*sr); y[:f]*=np.linspace(0,1,f)[:,None]; y[-f:]*=np.linspace(1,0,f)[:,None]
    i=int(dst*sr); out[i:i+n]+=y[:max(0,min(n,N-i))]
    log.append((src if kind=="d" else "orig%s"%(src,), dst, round(dst+n/sr,2)))
sf.write("de_v4.wav",np.clip(out,-1,1),sr)
for l in log: print(l)
