from typing import Optional

from pydantic import BaseModel, EmailStr

# Shared Properties.
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    codeforces_handle: Optional[str] = None
    current_class: Optional[str] = 'other'
    overall_score: Optional[int] = 0


# Properties to receive via API on creation.
class UserCreate(UserBase):
    email: EmailStr
    password: str
    codeforces_handle: str
    current_class: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
