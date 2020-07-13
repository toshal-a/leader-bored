from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

#------------------- Schemas for UserCodeForces----------------
# Properties to receive via API on creation.
class UserCodeforcesCreate(BaseModel):
    user_id: int
    codeforces_id: int
    percentile: float

# Properties to receive via API on update.
class UserCodeforcesUpdate(BaseModel):
    #user_id: int
    #codeforces_id: int
    percentile: float


#-------------------- Schemas for UserCodeChef ----------------
# Properties to receive via API on creation.
class UserCodechefCreate(BaseModel):
    user_id: int
    codechef_id: str
    percentile: float

# Properties to receive via API on update.
class UserCodechefUpdate(BaseModel):
    #user_id: int
    #codechef_id: str
    percentile: float