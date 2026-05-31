import json
from pathlib import Path
from app.core.config import get_settings
from app.pipeline.types import ScoredFacet
class ConsistencyValidator:
    def __init__(self)->None:
        p=Path(get_settings().data_dir)/'facet_relationships.json'; self.rel=json.loads(p.read_text()) if p.exists() else {'inverse':{},'correlated':{}}
    def validate(self,scores:list[ScoredFacet])->list[dict]:
        by={s.facet_id:s for s in scores}; alerts=[]
        for fid,others in self.rel.get('inverse',{}).items():
            for other in others:
                if fid in by and other in by and by[fid].score>=1 and by[other].score>=1: alerts.append({'type':'contradiction','severity':'high','facet_id':fid,'related_facet_id':other,'message':'Inverse facets both scored positive.'})
        for s in scores:
            if s.confidence<.45: s.review_flags.append('low_confidence'); alerts.append({'type':'review_flag','severity':'low','facet_id':s.facet_id,'message':'Low agreement.'})
        return alerts
