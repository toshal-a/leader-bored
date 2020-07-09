from sqlalchemy import Boolean, Column, Enum, Integer, String, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from leader_bored.db.base_class import Base

user_codechef = Table(
    "user_codechef", Base.metadata,
    Column('user_id',Integer, ForeignKey('users.id')),
    Column('codechef_id',String, ForeignKey('codechef.id'))
)

user_codeforces = Table(
    "user_codeforces", Base.metadata,
    Column('user_id',Integer, ForeignKey('users.id')),
    Column('codeforces_id',Integer, ForeignKey('codeforces.id'))
)