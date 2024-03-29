from typing import Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr

class ClassEnum(str,Enum):
    FE = 'FE'
    SE = 'SE'
    TE = 'TE'
    BE = 'BE'
    OTHER = 'Other'
# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    handle : Optional[str] = None
    class_type: ClassEnum = ClassEnum.OTHER


# Properties to receive via API on creation.
class UserCreate(UserBase):
    email: EmailStr
    password: str
    handle: str

# Properties to receive via API on update.
class UserUpdate(BaseModel):
    is_active: Optional[bool]=None
    password: Optional[str] = None
    percent: Optional[float] = None
    class_type: Optional[ClassEnum] = 'Other'

class UserEmail(BaseModel):
    email: EmailStr

class UserFeedback(BaseModel):
    username: Optional[str]
    title: str
    feedback: str

# Properties to return via API.
class UserHandle(BaseModel):
    handle : List[str]

class UserInDBBase(UserBase):
    id: Optional[int] = None
    avg_percent: Optional[float] = 0
    aggr_percent: Optional[float] = 0 
    contests_played: Optional[int] = 0

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass

class UserCodeforcesPlayed(BaseModel):
    codeforces_id: int
    contest_name: str
    contest_percentile: float
    contest_time: datetime

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    is_active: Optional[bool] = False
    is_superuser: bool = False
    hashed_password: str
    codechef_played: Optional[List] = []
    codeforces_played: Optional[List] = []

