import statistics
from typing import Any
from app.core.config import get_settings
from app.pipeline.stage2_scorer import TwoPassScorer
from app.pipeline.types import ScoredFacet
class ConfidenceEngine:
    def __init__(self,scorer:TwoPassScorer|None=None)->None: self.scorer=scorer or TwoPassScorer(); self.settings=get_settings()
    async def enrich(self,turn:dict[str,Any],context:dict[str,Any],facets:list[dict[str,Any]],base_scores:list[ScoredFacet])->list[ScoredFacet]:
        runs=[base_scores]
        for temp in (0.8,1.1)[:self.settings.confidence_ensemble_runs]: runs.append(await self.scorer.score(turn,context,facets,temp))
        maps=[{s.facet_id:s for s in r} for r in runs]
        for s in base_scores:
            vals=[m[s.facet_id].score for m in maps if s.facet_id in m]; st=statistics.pstdev(vals) if len(vals)>1 else 0.0; mean=statistics.mean(vals); s.agreement_score=round(vals.count(round(mean))/len(vals),3); s.confidence=round(max(.05,min(.99,1-st/2.5)),3); s.confidence_interval=[round(max(-2,mean-1.96*st),2),round(min(2,mean+1.96*st),2)]; s.raw_outputs['ensemble']={'scores':vals,'mean':round(mean,3),'stdev':round(st,3)}
        return base_scores
