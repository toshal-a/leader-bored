from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime


class CodeforcesContestEnum(str, Enum):
    CF = 'CF'
    IOI = 'IOI'
    ICPC = 'ICPC'

class CodeforcesContestStatus(str, Enum):
    BEFORE = 'BEFORE'
    CODING = 'CODING'
    PENDINGSYSTEMTEST = 'PENDING SYSTEM TEST'
    SYSTEMTEST= 'SYSTEM TEST'
    FINISHED = 'FINISHED'

# Shared properties.
class CodeforcesContestBase(BaseModel):
    id: Optional[int] = None
    contest_name: Optional[str] = None
    is_added:Optional[bool]=True
    starting_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    contest_type: CodeforcesContestEnum = CodeforcesContestEnum.CF
    contest_status: CodeforcesContestStatus = CodeforcesContestStatus.BEFORE

# Properties to receive via API on creation.
class CodeforcesContestCreate(CodeforcesContestBase):
    id: int
    contest_name: str
    duration_seconds: int
    contest_type: CodeforcesContestEnum
    contest_status: CodeforcesContestStatus

# Properties to receive via API on update.
class CodeforcesContestUpdate(BaseModel):
    is_added: bool
    added_at: Optional[datetime]
    reverted_at: Optional[datetime]
    
# Properties to return via API
class CodeforcesContestInDBBase(CodeforcesContestBase):
    is_added: bool
    added_at: Optional[datetime]
    reverted_at: Optional[datetime]
    class Config:
        orm_mode = True


# Additional properties to return via API
class CodeforcesContest(CodeforcesContestInDBBase):
    pass

class CodeforcesContestUserInfo(BaseModel):
    user_id: int
    codeforces_handle: str

# Additional properties stored in DB.
class CodeforcesContestInDB(CodeforcesContestInDBBase):
    updated_at: datetime
    users: Optional[List] = []
