from sqlalchemy import Boolean, Column, Enum, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from leader_bored.db.base_class import Base

class Users(Base):
    id = Column(Integer, primary_key=True)
    full_name = Column(String,nullable=False)
    email = Column(String, unique=True,nullable=False)
    hashed_password = Column(String, nullable=False)
    class_type = Column(Enum('FE','SE','TE','BE','Other',name="class_types"),server_default='Other')
    handle = Column(String,unique=True,nullable=False)
    rank = Column(Integer,default=None)
    avg_percent = Column(Float, default=0, nullable=True)
    aggr_percent = Column(Float, default=0, nullable=True)
    contests_played = Column(Integer, default=0, nullable=True)
    is_active = Column(Boolean(), default=False,nullable=False)
    is_superuser = Column(Boolean(), default=False,nullable=False)
    created_at = Column(DateTime,server_default=func.now())
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now())
    codechef_played = relationship("UserCodechef",back_populates="user")
    codeforces_played = relationship("UserCodeforces",back_populates="user")
