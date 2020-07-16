from sqlalchemy import Boolean, Column, Enum, Integer, String, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from leader_bored.db.base_class import Base

class UserCodechef(Base):
    __tablename__ = "user_codechef"
    user_id = Column(Integer, ForeignKey('users.id'), primary_key = True)
    codechef_id = Column(String, ForeignKey('codechef.id'), primary_key = True)
    percentile = Column(Float, default=0.0)
    user = relationship("Users", back_populates='codechef_played')
    contest = relationship("Codechef", back_populates='users')

class UserCodeforces(Base):
    __tablename__ = "user_codeforces"
    user_id = Column(Integer, ForeignKey('users.id'), primary_key = True)
    codeforces_id = Column(Integer, ForeignKey('codeforces.id'), primary_key = True)
    percentile = Column(Float, default=0.0)
    user = relationship("Users", back_populates='codeforces_played')
    contest = relationship("Codeforces", back_populates='users')