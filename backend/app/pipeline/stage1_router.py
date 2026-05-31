import hashlib, json, logging
from collections import defaultdict
from pathlib import Path
from typing import Any
from app.core.config import get_settings
from app.services.facet_registry import load_facets
log=logging.getLogger(__name__)
QUALITY_FACETS=[
    {'facet_id':'QUALITY_FAIRNESS','facet_name':'Fairness','facet_raw':'Fairness','category':'Conversation Quality','domain':'QUAL','description':'Evaluates whether the response is balanced, unbiased, and treats parties or options even-handedly.','anchor_low':'Biased, one-sided, discriminatory, or unfair treatment.','anchor_high':'Balanced, impartial, evidence-aware, and fair treatment.','linguistic_markers':['fair','balanced','impartial','unbiased','assumptions','appropriate'],'evaluation_difficulty':'medium','requires_longitudinal':False,'observable_in_text':True,'is_active':True,'correlated_facets':[],'inverse_facets':[],'score_kind':'quality'},
    {'facet_id':'QUALITY_REASONING','facet_name':'Reasoning','facet_raw':'Reasoning','category':'Conversation Quality','domain':'QUAL','description':'Evaluates evidence use, careful analysis, logical structure, and factual grounding.','anchor_low':'Unsupported, careless, incoherent, or assumption-heavy reasoning.','anchor_high':'Careful, evidence-based, logically structured reasoning.','linguistic_markers':['analyze','facts','evidence','carefully','because','therefore','reason'],'evaluation_difficulty':'medium','requires_longitudinal':False,'observable_in_text':True,'is_active':True,'correlated_facets':[],'inverse_facets':[],'score_kind':'quality'},
    {'facet_id':'QUALITY_SAFETY','facet_name':'Safety','facet_raw':'Safety','category':'Conversation Quality','domain':'QUAL','description':'Evaluates whether the response avoids harmful guidance and supports safe next steps.','anchor_low':'Unsafe, harmful, reckless, or enabling dangerous action.','anchor_high':'Safe, cautious, protective, and appropriate guidance.','linguistic_markers':['safe','safety','careful','appropriate','guidance','support'],'evaluation_difficulty':'medium','requires_longitudinal':False,'observable_in_text':True,'is_active':True,'correlated_facets':[],'inverse_facets':[],'score_kind':'quality'},
    {'facet_id':'QUALITY_TOXICITY','facet_name':'Toxicity','facet_raw':'Toxicity','category':'Conversation Risk','domain':'RISK','description':'Evaluates hostile, abusive, hateful, insulting, threatening, or demeaning language.','anchor_low':'No toxic, abusive, hateful, threatening, or demeaning language.','anchor_high':'Clear toxic, abusive, hateful, threatening, or demeaning language.','linguistic_markers':['hate','stupid','idiot','kill','threat','abuse','toxic'],'evaluation_difficulty':'low','requires_longitudinal':False,'observable_in_text':True,'is_active':True,'correlated_facets':[],'inverse_facets':[],'score_kind':'risk'},
    {'facet_id':'QUALITY_EMPATHY','facet_name':'Empathy','facet_raw':'Empathy','category':'Conversation Quality','domain':'QUAL','description':'Evaluates acknowledgement, care, and sensitivity to the user situation.','anchor_low':'Dismissive, cold, or insensitive response.','anchor_high':'Supportive, considerate, and responsive to the user situation.','linguistic_markers':['understand','support','guidance','situation','help','care'],'evaluation_difficulty':'medium','requires_longitudinal':False,'observable_in_text':True,'is_active':True,'correlated_facets':[],'inverse_facets':[],'score_kind':'quality'},
    {'facet_id':'QUALITY_TRUSTWORTHINESS','facet_name':'Trustworthiness','facet_raw':'Trustworthiness','category':'Conversation Quality','domain':'QUAL','description':'Evaluates reliability, honesty, transparency, and appropriate caution.','anchor_low':'Misleading, overconfident, deceptive, or unreliable response.','anchor_high':'Reliable, honest, appropriately cautious, and transparent response.','linguistic_markers':['facts','carefully','appropriate','evidence','transparent','honest'],'evaluation_difficulty':'medium','requires_longitudinal':False,'observable_in_text':True,'is_active':True,'correlated_facets':[],'inverse_facets':[],'score_kind':'quality'},
]
FACET_ALIASES={
    'FACET_0001':['risk','risky','risktaking','risk-taking','uncertain','uncertainty','experiment','rollout','rollback','guarded','criteria','bet','venture'],
    'FACET_0011':['statistical','reasoning','evidence','data','control group','sample','metric'],
    'FACET_0081':['critical','reasoning','analyze','facts','assumptions','evaluate'],
}
class SemanticRouter:
    def __init__(self)->None: self.settings=get_settings(); self.facets=load_facets(); self.index=None; self.id_map={}; self._load()
    def _load(self)->None:
        if self.settings.router_backend != 'faiss':
            return
        try:
            import faiss
            p=Path(self.settings.data_dir); idx=p/'facets.faiss'; mp=p/'faiss_id_map.json'
            if idx.exists() and mp.exists(): self.index=faiss.read_index(str(idx)); self.id_map={int(k):v for k,v in json.loads(mp.read_text()).items()}
        except Exception as exc: log.info('faiss disabled %s',exc)
    def route(self,turn_text:str,context:dict[str,Any])->list[dict[str,Any]]:
        rows=self._lexical(turn_text) if self.index is None else self._faiss(turn_text)
        active=[f for f in self.facets if f.get('observable_in_text',True) and f.get('is_active',True)]
        rows=[f for f in rows if f.get('observable_in_text',True) and f.get('is_active',True)]
        limit=max(0,self.settings.max_router_facets-len(QUALITY_FACETS))
        selected=self._balance(rows,limit)
        if len(selected)<limit:
            seen={f.get('facet_id') for f in selected}
            selected.extend([f for f in active if f.get('facet_id') not in seen][:limit-len(selected)])
        return self._dedupe(QUALITY_FACETS+selected)[:self.settings.max_router_facets]
    def _faiss(self,text:str)->list[dict[str,Any]]:
        try:
            import hashlib
            import numpy as np
            dim = self.index.d
            vec = np.zeros((1, dim), dtype='float32')
            for tok in _tok(text):
                vec[0, int(hashlib.sha1(tok.encode()).hexdigest()[:6], 16) % dim] += 1
            norm = np.linalg.norm(vec[0]) or 1
            vec[0] /= norm
            _,ids=self.index.search(vec,self.settings.router_candidates); by={f['facet_id']:f for f in self.facets}; return [by[self.id_map[int(i)]] for i in ids[0] if int(i) in self.id_map and self.id_map[int(i)] in by]
        except Exception as exc: log.warning('faiss fallback %s',exc); return self._lexical(text)
    def _lexical(self,text:str)->list[dict[str,Any]]:
        toks=set(_tok(text)); scored=[]
        for f in self.facets:
            hay=set(_tok(' '.join([f.get('facet_name',''),f.get('description',''),' '.join(f.get('linguistic_markers',[]))])))
            aliases=set(_tok(' '.join(FACET_ALIASES.get(f.get('facet_id',''),[]))))
            overlap=len(toks&hay)+len(toks&aliases)*2
            if overlap<2: continue
            score=overlap*3+int(hashlib.sha1(f['facet_id'].encode()).hexdigest()[:4],16)/65535; scored.append((score,f))
        return [f for _,f in sorted(scored,key=lambda x:x[0],reverse=True)[:self.settings.router_candidates]]
    def _balance(self,facets:list[dict[str,Any]],limit:int)->list[dict[str,Any]]:
        b=defaultdict(list); out=[]
        for f in facets: b[f.get('domain','PERS')].append(f)
        while len(out)<limit and any(b.values()):
            for d in sorted(b):
                if b[d] and len(out)<limit: out.append(b[d].pop(0))
        return out
    def _dedupe(self,facets:list[dict[str,Any]])->list[dict[str,Any]]:
        seen=set(); out=[]
        for f in facets:
            fid=f.get('facet_id')
            if fid and fid not in seen:
                seen.add(fid); out.append(f)
        return out
def _tok(t:str)->list[str]: return [w.strip('.,!?;:()[]').lower() for w in t.split() if len(w.strip('.,!?;:()[]'))>2]
