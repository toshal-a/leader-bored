from fastapi import APIRouter

from ..schemas.users import UserCreate
from ..crud import users

router = APIRouter()


@router.get("/users/all")
async def all_users():
    response = await users.get_all_users()
    return response


@router.get("/users/handles")
async def get_all_handles():
    response = await users.get_all_handles()
    return response


@router.get("/users/score/{uid}")
async def get_user_score(uid: int):
    response = await users.get_user_score(uid)
    return response


@router.get("/users/{uid}")
async def get_user(uid: int):
    response = await users.get_user_by_id(uid)
    return response


@router.post("/users")
async def add_user(user: UserCreate):
    response = await users.create_user(user)
    return response


@router.post("/users/score/{uid}")
async def update_score(uid: int, score: int = 0):
    response = await users.update_user_score(uid, score)
    return response


@router.delete("/users/{uid}")
async def delete_user(uid: int):
    response = await users.delete_user_by_id(uid)
    return response


def init_app(app):
    app.include_router(router)
