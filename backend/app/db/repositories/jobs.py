from typing import Any
from sqlalchemy.orm import Session, selectinload
from app.models.entities import Conversation, EvaluationJob, TurnResult, FacetScore
class ConversationRepository:
    def __init__(self,db:Session): self.db=db
    def list(self)->list[Conversation]: return self.db.query(Conversation).order_by(Conversation.created_at.desc()).all()
    def get(self,cid:str)->Conversation|None: return self.db.get(Conversation,cid)
    def add(self,item:Conversation)->Conversation: self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def delete(self,cid:str)->bool:
        item=self.get(cid)
        if not item: return False
        self.db.delete(item); self.db.commit(); return True
class EvaluationRepository:
    def __init__(self,db:Session): self.db=db
    def add_job(self,job:EvaluationJob)->EvaluationJob: self.db.add(job); self.db.commit(); self.db.refresh(job); return job
    def get_job(self,job_id:str)->EvaluationJob|None: return self.db.query(EvaluationJob).options(selectinload(EvaluationJob.turn_results).selectinload(TurnResult.facet_scores)).filter(EvaluationJob.id==job_id).first()
    def update_job(self,job_id:str,**fields:Any)->None:
        job=self.db.get(EvaluationJob,job_id)
        if job:
            for k,v in fields.items(): setattr(job,k,v)
            self.db.commit()
    def add_turn_result(self,turn:TurnResult,scores:list[FacetScore])->TurnResult:
        self.db.add(turn); self.db.flush()
        for score in scores: score.turn_result_id=turn.id; self.db.add(score)
        self.db.commit(); self.db.refresh(turn); return turn
