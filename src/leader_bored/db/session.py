from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from leader_bored.core import settings

engine = create_engine(settings.DB_DSN, pool_pre_ping=True,echo_pool=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
