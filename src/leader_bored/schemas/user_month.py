from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr

class MonthEnum(Enum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

class ClassEnum(str,Enum):
    FE = 'FE'
    SE = 'SE'
    TE = 'TE'
    BE = 'BE'
    OTHER = 'Other'

class UserCodeforcesMonthBase(BaseModel):
    user_id: Optional[int] = None
    month: Optional[MonthEnum] = None
    year: Optional[int] = None
    avg_percentile: Optional[float] = None
    aggr_percentile: Optional[float] = None
    contests_played: Optional[int] = None


# Properties to receive via API on creation.
class UserCodeforcesMonthCreate(UserCodeforcesMonthBase):
    user_id: int
    month: MonthEnum
    year: int

# Properties to receive via API on update.
class UserCodeforcesMonthUpdate(BaseModel):
    percentile: Optional[float] = None


# Properties to return via API.
class UserCodeforcesMonth(UserCodeforcesMonthBase):
    class Config:
        orm_mode = True

# Additional properties to return via API
class UserInfoCodeforcesMonth(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    handle : Optional[str] = None
    class_type: ClassEnum = ClassEnum.OTHER
    avg_percentile: Optional[float] = None
    aggr_percentile: Optional[float] = None
    contests_played: Optional[int] = None
