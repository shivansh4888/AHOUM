from app.pipeline.stage1_router import SemanticRouter
from app.core.config import get_settings
from app.pipeline.stage4_validator import ConsistencyValidator
def test_router_bound(): assert len(SemanticRouter().route('fair evidence and calm leadership',{}))<=get_settings().max_router_facets
def test_router_default_scores_300_facets(): assert len(SemanticRouter().route('short turn',{}))==300
def test_validator(): assert ConsistencyValidator().validate([])==[]
