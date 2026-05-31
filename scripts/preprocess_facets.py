#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,re,struct
from pathlib import Path
DOMAINS=['PERS','COGS','EMOT','SOCL','LANG','ETHI','SPRT','PHYS','BEHV','LEAD','PSYC']
K={'COGS':['reason','logic','statistical','technical','common-sense'],'EMOT':['emotion','merry','morose','discontent','compassion'],'SOCL':['relationship','social','aloof','democratic'],'ETHI':['ethic','fair','moral','cunning'],'SPRT':['spiritual','faith'],'PHYS':['physical','fatigue'],'BEHV':['risk','adventure','hesitation','behavior'],'LEAD':['leadership','leader','control'],'PSYC':['self','naivety','overprotect'],'LANG':['language','communication']}
def clean(x): return re.sub(r'\s+',' ',re.sub(r'^\s*\d+[.)-]?\s*','',x).strip().strip(':'))
def dom(name,cat):
    t=(name+' '+cat).lower()
    for d,ks in K.items():
        if any(k in t for k in ks): return d
    return DOMAINS[int(hashlib.sha1(t.encode()).hexdigest()[:2],16)%len(DOMAINS)]
def marks(n): return list(dict.fromkeys([p.lower() for p in re.split(r'[-/\s]+',n) if len(p)>3]+(['evidence','because','data'] if 'reason' in n.lower() else [])+(['team','delegate','decision'] if 'lead' in n.lower() else [])))[:10]
def score_kind(name,cat):
    t=(name+' '+cat).lower()
    if any(w in t for w in ['disrespect','dishonesty','fatigue','depression','psychoticism','neuroticism','pain','burnout','sloth','desperation','discontent','moroseness','negative','immaturity','inattentiveness','inefficiency','impractical','passive-aggressive']):
        return 'risk'
    return 'quality'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',default='Facets Assignment.csv'); ap.add_argument('--out',default='data'); a=ap.parse_args(); rows=[]
    with open(a.input,newline='',encoding='utf-8-sig') as f:
        for r in csv.reader(f):
            if r and r[0].strip(): rows.append(r[0].strip())
    facets=[]; cat='General'
    for raw in rows:
        if raw.lower()=='facets': continue
        if raw.endswith(':') and not re.match(r'^\s*\d+',raw): cat=clean(raw); continue
        name=clean(raw); d=dom(name,cat); obs=not any(x in name.lower() for x in ['soul','genetic','destiny','blood']); fid=f'FACET_{len(facets)+1:04d}'
        facets.append({'facet_id':fid,'facet_raw':raw,'facet_name':name,'category':cat,'domain':d,'description':f'Evaluates observable evidence of {name.lower()} in a conversation turn without inferring beyond text.','anchor_low':f'Clear evidence opposing or lacking {name.lower()}.','anchor_high':f'Clear evidence expressing strong {name.lower()}.','linguistic_markers':marks(name),'evaluation_difficulty':'high' if not obs else ('medium' if len(name.split())>2 else 'low'),'requires_longitudinal':any(w in name.lower() for w in ['consistency','improvement','habit']),'observable_in_text':obs,'is_active':True,'score_kind':score_kind(name,cat),'correlated_facets':[],'inverse_facets':[]})
    rel={'inverse':{},'correlated':{}}
    pairs=[('merriness','moroseness'),('risk','hesitation'),('naivety','cunning'),('aloof','emotional')]
    for f in facets:
        corr=[g['facet_id'] for g in facets if g is not f and g['domain']==f['domain']][:5]; f['correlated_facets']=corr
        if corr: rel['correlated'][f['facet_id']]=corr
        inv=[g['facet_id'] for g in facets if g is not f and any((a in f['facet_name'].lower() and b in g['facet_name'].lower()) or (b in f['facet_name'].lower() and a in g['facet_name'].lower()) for a,b in pairs)][:5]; f['inverse_facets']=inv
        if inv: rel['inverse'][f['facet_id']]=inv
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True); (out/'facets_enriched.json').write_text(json.dumps(facets,indent=2)); (out/'facet_relationships.json').write_text(json.dumps(rel,indent=2)); (out/'faiss_id_map.json').write_text(json.dumps({i:f['facet_id'] for i,f in enumerate(facets)},indent=2))
    dim=384; vec=[[0.0 for _ in range(dim)] for _ in facets]
    for i,f in enumerate(facets):
        for tok in re.findall(r'[a-zA-Z]+',(f['facet_name']+' '+f['description']).lower()): vec[i][int(hashlib.sha1(tok.encode()).hexdigest()[:6],16)%dim]+=1.0
        n=math.sqrt(sum(x*x for x in vec[i])) or 1.0
        vec[i]=[x/n for x in vec[i]]
    try:
        import numpy as np
        import faiss
        arr=np.array(vec,dtype='float32'); idx=faiss.IndexFlatIP(dim); idx.add(arr); faiss.write_index(idx,str(out/'facets.faiss'))
    except Exception:
        with (out/'facets_vectors.bin').open('wb') as fh:
            fh.write(struct.pack('II',len(vec),dim))
            for row in vec:
                fh.write(struct.pack(f'{dim}f',*row))
        (out/'facets.faiss').write_bytes(b'fallback vectors in facets_vectors.bin')
    print(f'exported {len(facets)} facets')
if __name__=='__main__': main()
