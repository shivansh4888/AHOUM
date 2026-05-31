from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import Base, engine
from app.models import entities  # noqa
configure_logging(); s=get_settings(); app=FastAPI(title=s.app_name,version='1.0.0',description='Conversation evaluation across behavioral facets.')
app.add_middleware(CORSMiddleware,allow_origins=s.origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*']); app.include_router(router)
@app.on_event('startup')
def startup()->None: Base.metadata.create_all(bind=engine)
@app.get('/health')
def health()->dict[str,str]: return {'status':'ok'}
