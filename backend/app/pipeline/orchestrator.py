import logging
from typing import Any
from sqlalchemy.orm import Session
from app.db.repositories.jobs import EvaluationRepository
from app.models.entities import FacetScore, TurnResult
from app.pipeline.stage0_analyzer import ContextAnalyzer
from app.pipeline.stage1_router import SemanticRouter
from app.pipeline.stage2_scorer import TwoPassScorer
from app.pipeline.stage3_ensemble import ConfidenceEngine
from app.pipeline.stage4_validator import ConsistencyValidator
from app.services.progress import progress_hub
log=logging.getLogger(__name__)
class EvaluationOrchestrator:
    def __init__(self,db:Session)->None: self.repo=EvaluationRepository(db); self.analyzer=ContextAnalyzer(); self.router=SemanticRouter(); self.scorer=TwoPassScorer(); self.conf=ConfidenceEngine(self.scorer); self.val=ConsistencyValidator()
    async def run(self,job_id:str,turns:list[dict[str,Any]])->dict[str,Any]:
        await progress_hub.publish(job_id,'status','Evaluation started'); self.repo.update_job(job_id,status='running',progress=.02); summary={'turns':[]}; hist=[]
        try:
            for i,turn in enumerate(turns):
                ctx=await self.analyzer.analyze(turns,turn,hist); facets=self.router.route(turn.get('text',''),ctx); base=await self.scorer.score(turn,ctx,facets); scores=await self.conf.enrich(turn,ctx,facets,base); alerts=self.val.validate(scores)
                tr=TurnResult(job_id=job_id,turn_index=i,speaker=turn.get('speaker','user'),text=turn.get('text',''),context_analysis=ctx,routed_facets=[f['facet_id'] for f in facets],consistency_alerts=alerts)
                dbs=[FacetScore(facet_id=s.facet_id,facet_name=s.facet_name,domain=s.domain,score=s.score,confidence=s.confidence,confidence_interval=s.confidence_interval,agreement_score=s.agreement_score,reasoning=s.reasoning,adjustment=s.adjustment,raw_outputs=s.raw_outputs,review_flags=s.review_flags) for s in scores]
                self.repo.add_turn_result(tr,dbs); payload={'turn_index':i,'scores':[s.__dict__ for s in scores],'alerts':alerts,'context':ctx}; summary['turns'].append(payload); hist.append(turn); self.repo.update_job(job_id,progress=(i+1)/max(1,len(turns))*.96); await progress_hub.publish(job_id,'partial_result',f'Turn {i+1} scored',payload)
            self.repo.update_job(job_id,status='complete',progress=1,result_summary=summary); await progress_hub.publish(job_id,'complete','Evaluation complete',{'job_id':job_id}); return summary
        except Exception as exc:
            log.exception('evaluation failed'); self.repo.update_job(job_id,status='failed',error=str(exc)); await progress_hub.publish(job_id,'error',str(exc)); raise
