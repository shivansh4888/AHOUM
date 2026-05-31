from dataclasses import dataclass, field
from typing import Any
@dataclass
class ScoredFacet:
    facet_id:str; facet_name:str; domain:str; score:int; confidence:float=0.0; confidence_interval:list[float]=field(default_factory=list); agreement_score:float=0.0; reasoning:str=''; adjustment:str=''; raw_outputs:dict[str,Any]=field(default_factory=dict); review_flags:list[str]=field(default_factory=list)
