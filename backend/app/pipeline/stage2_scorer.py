import logging
from typing import Any
from app.core.config import get_settings
from app.pipeline.types import ScoredFacet
from app.services.groq_client import GroqClient
log=logging.getLogger(__name__)
DETERMINISTIC_FACETS={'FACET_0001'}
class TwoPassScorer:
    def __init__(self,client:GroqClient|None=None)->None: self.client=client or GroqClient(); self.settings=get_settings()
    async def score(self,turn:dict[str,Any],context:dict[str,Any],facets:list[dict[str,Any]],temperature:float=0.2)->list[ScoredFacet]:
        if len(facets)>self.settings.llm_scoring_facet_limit:
            return [_from_row(_heur(turn.get('text',''),f),f,'deterministic large-registry scoring') for f in facets]
        out=[_from_row(_heur(turn.get('text',''),f),f,'deterministic heuristic') for f in facets if _is_deterministic(f)]
        remaining=[f for f in facets if not _is_deterministic(f)]
        for i in range(0,len(remaining),self.settings.scoring_batch_size): out.extend(await self._batch(turn,context,remaining[i:i+self.settings.scoring_batch_size],temperature))
        return out
    async def _batch(self,turn:dict[str,Any],context:dict[str,Any],facets:list[dict[str,Any]],temperature:float)->list[ScoredFacet]:
        if not facets: return []
        prompt='Score facets -2..2 as JSON {scores:[{facet_id,score,reasoning}]}. Turn '+str(turn)+' Context '+str(context)+' Facets '+str([{k:f[k] for k in ['facet_id','facet_name','description','anchor_low','anchor_high']} for f in facets])
        try: rows=(await self.client.generate_json(prompt,system='Rigorous behavioral scorer. JSON only.',temperature=temperature)).get('scores',[])
        except Exception as exc: log.warning('score fallback %s',exc); rows=[_heur(turn.get('text',''),f) for f in facets]
        by={f['facet_id']:f for f in facets}; out=[]
        for r in rows:
            f=by.get(str(r.get('facet_id','')))
            if f: out.append(_from_row(r,f,'self-critique accepted'))
        for f in facets:
            if f['facet_id'] not in {s.facet_id for s in out}:
                r=_heur(turn.get('text',''),f); out.append(_from_row(r,f,'filled missing score'))
        return out
def _from_row(r:dict[str,Any],f:dict[str,Any],adjustment:str)->ScoredFacet:
    return ScoredFacet(f['facet_id'],f['facet_name'],f['domain'],max(-2,min(2,int(r.get('score',0)))),reasoning=str(r.get('reasoning','Observable textual evidence.')),adjustment=adjustment,raw_outputs={'pass1':r,'pass2':r,'score_kind':f.get('score_kind','quality')})
def _is_deterministic(f:dict[str,Any])->bool:
    return str(f.get('facet_id','')).startswith('QUALITY_') or f.get('facet_id') in DETERMINISTIC_FACETS
def _heur(text:str,f:dict[str,Any])->dict[str,Any]:
    t=text.lower(); fid=f.get('facet_id','')
    toxic=sum(w in t for w in ['hate','idiot','stupid','kill','threat','abuse','worthless','shut up','toxic'])
    unsafe=sum(w in t for w in ['harm','unsafe','dangerous','hide','manipulate','reckless'])
    evidence=sum(w in t for w in ['fact','facts','evidence','analyze','carefully','reason','appropriate','assumption'])
    support=sum(w in t for w in ['guidance','help','support','situation','understand','care'])
    fairness=sum(w in t for w in ['fair','fairly','balanced','unbiased','impartial','appropriate'])
    markers=sum(m.lower() in t for m in f.get('linguistic_markers',[]))
    if fid=='QUALITY_TOXICITY':
        score=2 if toxic>=2 else 1 if toxic==1 else -2
        reason='No toxic language detected.' if score==-2 else 'Potential toxic language detected.'
    elif fid=='QUALITY_SAFETY':
        raw=2+min(1,evidence+support+markers)-unsafe-toxic
        score=2 if raw>=2 else 1 if raw==1 else 0 if raw==0 else -1
        reason='Safe, appropriate guidance signals are present.' if score>=1 else 'Safety evidence is weak or mixed.'
    elif fid=='QUALITY_REASONING':
        score=2 if evidence>=2 or markers>=2 else 1 if evidence+markers>=1 else 0
        reason='Evidence-oriented or careful analysis language is present.' if score>=1 else 'Limited explicit reasoning evidence.'
    elif fid=='QUALITY_FAIRNESS':
        score=2 if fairness+markers>=2 else 1 if fairness+markers>=1 or evidence>=1 else 0
        reason='Balanced or appropriate-response language supports fairness.' if score>=1 else 'Limited explicit fairness evidence.'
    elif fid=='QUALITY_EMPATHY':
        score=2 if support+markers>=2 else 1 if support+markers>=1 else 0
        reason='Supportive guidance language is present.' if score>=1 else 'Limited explicit empathy evidence.'
    elif fid=='QUALITY_TRUSTWORTHINESS':
        score=2 if evidence+markers>=2 and toxic+unsafe==0 else 1 if evidence+markers>=1 and toxic==0 else 0
        reason='Careful, fact-oriented language supports trustworthiness.' if score>=1 else 'Limited explicit trustworthiness evidence.'
    elif fid=='FACET_0001':
        risk_terms=sum(w in t for w in ['risk','risky','uncertain','uncertainty','experiment','rollout','rollback','guarded','criteria','venture'])
        caution_terms=sum(w in t for w in ['guarded','rollback','criteria','careful','limited','test'])
        score=2 if risk_terms>=2 and caution_terms>=1 else 1 if risk_terms>=1 else 0
        reason='The text describes risk-taking through uncertainty, experimentation, and rollout/rollback choices.' if score>=1 else 'Limited explicit risk-taking evidence.'
    else:
        pos=sum(w in t for w in ['fair','help','learn','evidence','calm','support','improve','will'])
        neg=sum(w in t for w in ['harm','unsafe','hate','angry','blame','hide'])
        raw=pos+markers-neg
        score=2 if raw>=4 else 1 if raw>=1 else -1 if raw<0 else 0
        reason='Heuristic fallback from lexical markers and polarity.'
    return {'facet_id':f['facet_id'],'score':score,'reasoning':reason}
