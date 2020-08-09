from sqlalchemy import Boolean, Column, Enum, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from leader_bored.db.base_class import Base

class UserCodeforcesMonth(Base):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    month = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    avg_percentile = Column(Float, default=0, nullable=True)
    aggr_percentile = Column(Float, default=0, nullable=True)
    contests_played = Column(Integer, default=0, nullable=True)
    user = relationship("Users", back_populates="month_stats", foreign_keys=[user_id])