from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env', extra='ignore')
    app_name:str='ConvEval-300'; environment:str=Field('development',alias='ENVIRONMENT')
    database_url:str=Field('sqlite:///./conveval.db',alias='DATABASE_URL')
    redis_url:str=Field('redis://redis:6379/0',alias='REDIS_URL')
    groq_api_key:str=Field('',alias='GROQ_API_KEY')
    groq_base_url:str=Field('https://api.groq.com/openai/v1',alias='GROQ_BASE_URL')
    groq_model:str=Field('llama-3.1-8b-instant',alias='GROQ_MODEL')
    secondary_model:str=Field('llama-3.1-8b-instant',alias='SECONDARY_MODEL')
    router_backend:str=Field('lexical',alias='ROUTER_BACKEND')
    data_dir:str=Field('data',alias='DATA_DIR'); cors_origins:str=Field('http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:8080,http://127.0.0.1:8080',alias='CORS_ORIGINS')
    router_candidates:int=Field(150,alias='ROUTER_CANDIDATES')
    max_router_facets:int=Field(300,alias='MAX_ROUTER_FACETS')
    scoring_batch_size:int=Field(15,alias='SCORING_BATCH_SIZE')
    confidence_ensemble_runs:int=Field(2,alias='CONFIDENCE_ENSEMBLE_RUNS')
    llm_scoring_facet_limit:int=Field(60,alias='LLM_SCORING_FACET_LIMIT')
    request_timeout_seconds:int=Field(120,alias='REQUEST_TIMEOUT_SECONDS')
    @property
    def origins(self)->list[str]: return [x.strip() for x in self.cors_origins.split(',') if x.strip()]
@lru_cache
def get_settings()->Settings: return Settings()
