from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime


class ContestEnum(str, Enum):
    CF = 'CF'
    IOI = 'IOI'
    ICPC = 'ICPC'

# Shared properties
class ContestBase(BaseModel):
    id: Optional[int] = None
    contest_name: Optional[str] = None
    is_added:Optional[bool]=True
    starting_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    contest_type: ContestEnum = ContestEnum.CF

# Properties to receive via API on creation.
class ContestCreate(ContestBase):
    id: int
    contest_name: str
    duration_seconds: int
    contest_type: ContestEnum

# Properties to receive via API on update
class ContestUpdate(BaseModel):
    is_added: bool
    added_at: Optional[datetime]
    reverted_at: Optional[datetime]
    
# Properties to return via API
class ContestInDBBase(ContestBase):
    is_added: bool
    added_at: Optional[datetime]
    reverted_at: Optional[datetime]
    class Config:
        orm_mode = True


# Additional properties to return via API
class Contest(ContestInDBBase):
    pass


# Additional properties stored in DB
class ContestInDB(ContestInDBBase):
    updated_at: datetime
