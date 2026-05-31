import logging
from typing import Any
from app.services.groq_client import GroqClient
log=logging.getLogger(__name__)
DEFAULT={'primary_emotion':'neutral','secondary_emotions':[],'intent':'inform','topics':[],'linguistic_style':'plain','power_dynamic':'balanced','key_phrases':[],'notable_absences':[],'consistency_with_prior':'insufficient history','brief_summary':''}
class ContextAnalyzer:
    def __init__(self,client:GroqClient|None=None)->None: self.client=client or GroqClient()
    async def analyze(self,conversation:list[dict[str,Any]],current_turn:dict[str,Any],history:list[dict[str,Any]])->dict[str,Any]:
        prompt='Return strict JSON for primary_emotion, secondary_emotions, intent, topics, linguistic_style, power_dynamic, key_phrases, notable_absences, consistency_with_prior, brief_summary. History: '+str(history[-8:])+' Current: '+str(current_turn)
        try: return {**DEFAULT, **await self.client.generate_json(prompt,system='JSON conversation analyst.',temperature=0.1)}
        except Exception as exc:
            log.warning('stage0 fallback %s',exc); text=current_turn.get('text',''); keys=[w.strip('.,!?').lower() for w in text.split() if len(w)>4][:8]; return {**DEFAULT,'topics':keys,'key_phrases':keys[:5],'brief_summary':text[:220]}
