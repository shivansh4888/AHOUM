import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db.repositories.jobs import ConversationRepository, EvaluationRepository
from app.db.session import get_db
from app.models.entities import Conversation, EvaluationJob, FacetScore
from app.schemas.api import ConversationCreate, EvaluationAccepted, EvaluationRequest, FacetCreate
from app.services.facet_registry import add_facet, filter_facets, get_facet
from app.services.progress import progress_hub
from app.workers.tasks import evaluate_conversation
router=APIRouter()
@router.post('/api/evaluate',response_model=EvaluationAccepted,status_code=202)
def evaluate(req:EvaluationRequest,db:Session=Depends(get_db))->EvaluationAccepted:
    turns=[t.model_dump() for t in req.turns] if req.turns else None; conv_id=req.conversation_id
    if conv_id:
        conv=ConversationRepository(db).get(conv_id)
        if not conv: raise HTTPException(404,'conversation not found')
        turns=conv.turns
    if not turns: raise HTTPException(400,'turns or conversation_id required')
    job_id=uuid.uuid4().hex; EvaluationRepository(db).add_job(EvaluationJob(id=job_id,conversation_id=conv_id,status='queued',request_payload={'title':req.title,'turns':turns}))
    evaluate_conversation.delay(job_id,turns); return EvaluationAccepted(job_id=job_id,status='queued')
@router.get('/api/results/{job_id}')
def result(job_id:str,db:Session=Depends(get_db))->dict:
    job=EvaluationRepository(db).get_job(job_id)
    if not job: raise HTTPException(404,'job not found')
    return {'id':job.id,'status':job.status,'progress':job.progress,'error':job.error,'turn_results':[{'turn_index':t.turn_index,'speaker':t.speaker,'text':t.text,'context_analysis':t.context_analysis,'routed_facets':t.routed_facets,'consistency_alerts':t.consistency_alerts,'facet_scores':[_score_payload(s) for s in t.facet_scores]} for t in job.turn_results]}
@router.get('/api/facets')
def facets(search:str|None=None,domain:str|None=None,observable:bool|None=Query(default=None))->list[dict]: return filter_facets(search,domain,observable)
@router.post('/api/facets',status_code=201)
def create_facet(req:FacetCreate)->dict: return add_facet(req.model_dump())
@router.get('/api/facets/{facet_id}')
def facet(facet_id:str)->dict:
    f=get_facet(facet_id)
    if not f: raise HTTPException(404,'facet not found')
    return f
@router.get('/api/conversations')
def conversations(db:Session=Depends(get_db))->list[dict]: return [{'id':c.id,'title':c.title,'turns':c.turns,'tags':c.tags,'created_at':c.created_at.isoformat()} for c in ConversationRepository(db).list()]
@router.post('/api/conversations',status_code=201)
def create_conversation(req:ConversationCreate,db:Session=Depends(get_db))->dict:
    conv=Conversation(id=uuid.uuid4().hex,title=req.title,turns=[t.model_dump() for t in req.turns],tags=req.tags); ConversationRepository(db).add(conv); return {'id':conv.id,'title':conv.title,'turns':conv.turns,'tags':conv.tags,'created_at':conv.created_at.isoformat()}
@router.delete('/api/conversations/{conversation_id}',status_code=204)
def delete_conversation(conversation_id:str,db:Session=Depends(get_db))->None:
    if not ConversationRepository(db).delete(conversation_id): raise HTTPException(404,'conversation not found')
@router.websocket('/ws/progress/{job_id}')
async def ws_progress(websocket:WebSocket,job_id:str)->None:
    await progress_hub.connect(job_id,websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: await progress_hub.disconnect(job_id,websocket)
def _score_payload(s:FacetScore)->dict:
    display_score=max(-2,min(2,int(s.score)))
    score_kind=(s.raw_outputs or {}).get('score_kind','quality')
    quality_score=-display_score if score_kind=='risk' else display_score
    return {'facet_id':s.facet_id,'facet_name':s.facet_name,'domain':s.domain,'score':display_score,'display_score':display_score,'quality_score':quality_score,'score_kind':score_kind,'confidence':s.confidence,'confidence_interval':s.confidence_interval,'agreement_score':s.agreement_score,'reasoning':s.reasoning,'adjustment':s.adjustment,'review_flags':s.review_flags,'raw_outputs':s.raw_outputs}
