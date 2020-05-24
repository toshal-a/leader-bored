from fastapi import APIRouter
from pydantic import BaseModel

from ..models.users import User
from ..schemas.users import UserCreate

router = APIRouter()

@router.get("/users/{uid}")
async def get_user(uid: int):
    user = await User.get_or_404(uid)
    return user.to_dict()

@router.post("/users")
async def add_user(user: UserCreate):
    rv = await User.create(
        full_name=user.full_name,
        email=user.email,
        hashed_password=user.password,
        codeforces_handle=user.codeforces_handle,
    )
    return rv.to_dict()

@router.delete("/users/{uid}")
async def delete_user(uid: int):
    user = await User.get_or_404(uid)
    await user.delete()
    return dict(id=uid)

def init_app(app):
    app.include_router(router)
