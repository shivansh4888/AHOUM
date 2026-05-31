from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.core.config import get_settings
class Base(DeclarativeBase): pass
engine=create_engine(get_settings().database_url, pool_pre_ping=True, connect_args={'check_same_thread':False} if get_settings().database_url.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False,expire_on_commit=False)
def get_db()->Generator[Session,None,None]:
    db=SessionLocal()
    try: yield db
    finally: db.close()
