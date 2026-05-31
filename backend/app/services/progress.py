import asyncio, json
from collections import defaultdict
from typing import Any
from fastapi import WebSocket
class ProgressHub:
    def __init__(self)->None: self.clients:dict[str,set[WebSocket]]=defaultdict(set); self.history:dict[str,list[dict[str,Any]]]=defaultdict(list); self.lock=asyncio.Lock()
    async def connect(self,job_id:str,ws:WebSocket)->None:
        await ws.accept(); self.clients[job_id].add(ws)
        for e in self.history[job_id][-20:]: await ws.send_json(e)
    async def disconnect(self,job_id:str,ws:WebSocket)->None: self.clients[job_id].discard(ws)
    async def publish(self,job_id:str,event_type:str,message:str|None=None,payload:dict[str,Any]|None=None)->None:
        e={'type':event_type,'job_id':job_id,'message':message,'payload':payload or {}}; self.history[job_id].append(e)
        for ws in list(self.clients[job_id]):
            try: await ws.send_text(json.dumps(e))
            except Exception: self.clients[job_id].discard(ws)
progress_hub=ProgressHub()
