from celery import Celery
from app.core.config import get_settings
s=get_settings(); celery_app=Celery('conveval',broker=s.redis_url,backend=s.redis_url,include=['app.workers.tasks']); celery_app.conf.update(task_track_started=True,task_serializer='json',result_serializer='json',accept_content=['json'])
