from typing import Any, Literal
from pydantic import BaseModel, Field
class ConversationTurn(BaseModel): speaker:str='user'; text:str=Field(min_length=1); timestamp:str|None=None
class ConversationCreate(BaseModel): title:str; turns:list[ConversationTurn]; tags:list[str]=[]
class EvaluationRequest(BaseModel): conversation_id:str|None=None; title:str='Ad hoc evaluation'; turns:list[ConversationTurn]|None=None
class EvaluationAccepted(BaseModel): job_id:str; status:str
class FacetCreate(BaseModel):
    facet_name:str=Field(min_length=1)
    domain:str=Field(min_length=2,max_length=12)
    description:str=Field(min_length=1)
    category:str='Custom'
    anchor_low:str|None=None
    anchor_high:str|None=None
    linguistic_markers:list[str]=Field(default_factory=list)
    evaluation_difficulty:Literal['low','medium','high']='medium'
    requires_longitudinal:bool=False
    observable_in_text:bool=True
    is_active:bool=True
class ProgressEvent(BaseModel): type:Literal['status','partial_result','complete','error']; job_id:str; message:str|None=None; payload:dict[str,Any]={}
