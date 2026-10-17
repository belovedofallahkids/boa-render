import json,os,sys
p=os.path.join(os.path.dirname(__file__),'..','assets','img_registry_15_25.json')
reg=json.load(open(p)) if os.path.exists(p) else {}
for l in open(sys.argv[1]):
    if l.strip(): k,v=l.split(); reg[k]=v
json.dump(reg,open(p,'w'),indent=1); print(len(reg))
