from sqlalchemy import Boolean, Column, Enum, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from leader_bored.db.base_class import Base

class Codechef(Base):
    id = Column(String, primary_key=True)
    contest_name = Column(String, nullable=False)
    starting_at = Column(DateTime, nullable = True)
    duration_seconds= Column(Integer, default= 0, nullable = False)
    contest_type = Column(Enum('LONG', 'COOKOFF', 'LUNCHTIME', name="codechef_types"))
    contest_status = Column(Enum('BEFORE','CODING','PENDING SYSTEM TEST','SYSTEM TEST','FINISHED',name="codechef_status_types"))
    added_at = Column(DateTime, server_default=func.now(), nullable= True)
    reverted_at = Column(DateTime, default=None, nullable = True)
    is_added = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now())
    users = relationship("Users",secondary="user_codechef",back_populates="codechef_played")
