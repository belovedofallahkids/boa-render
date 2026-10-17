import json,sys
f=json.load(open(sys.argv[1])); clips=[]; prev=None
for seg,nid in f['nodes'].items():
    sc=seg[1]
    gap=0 if prev is None else (0.6 if sc==prev else 1.2)
    clips.append({"gap_before":gap,"modality":"audio","source":{"template_node_id":nid}}); prev=sc
print(json.dumps({"tracks":[{"clips":clips,"volume":1,"mute":False}]}))
