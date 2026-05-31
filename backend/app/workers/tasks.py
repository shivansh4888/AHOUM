import asyncio
from app.db.session import SessionLocal
from app.pipeline.orchestrator import EvaluationOrchestrator
from app.workers.celery_app import celery_app
@celery_app.task(name='evaluate_conversation',autoretry_for=(Exception,),retry_backoff=True,retry_kwargs={'max_retries':2})
def evaluate_conversation(job_id:str,turns:list[dict])->dict:
    db=SessionLocal()
    try: return asyncio.run(EvaluationOrchestrator(db).run(job_id,turns))
    finally: db.close()
