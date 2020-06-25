from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from leader_bored import crud, models, schemas
from leader_bored.core import depends, settings
from leader_bored.utils import users_utils

router = APIRouter()


@router.get("/", dependencies=[Depends(depends.verify_token)], response_model=List[schemas.User])
async def read_users(
    db: Session = Depends(depends.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/handle", dependencies=[Depends(depends.verify_token)], response_model=schemas.UserHandle)
async def read_user_handles(
    db: Session = Depends(depends.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve user handles.
    """
    handles = crud.user.get_multi_handle(db)

    return dict(handle=[getattr(handle,'handle') for handle in handles])

@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: Session = Depends(depends.get_db),
    user_in: schemas.UserCreate
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    users_utils.send_new_account_email(user_in.email, user_in.handle)

    return user

@router.get("/{user_id}",dependencies=[Depends(depends.verify_token)], response_model=schemas.User)
async def read_user_by_id(
    user_id: int,
    db: Session = Depends(depends.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    return user


@router.put("/{user_id}",dependencies=[Depends(depends.verify_token)], response_model=schemas.User)
async def update_user(
    *,
    db: Session = Depends(depends.get_db),
    user_id: int,
    user_in: schemas.UserUpdate
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}",dependencies=[Depends(depends.verify_token)], response_model=schemas.User)
async def delete_user(
    *,
    db: Session = Depends(depends.get_db),
    user_id: int
) -> Any:
    """
    Delete a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.remove(db,id=user_id)
    return user

@router.get("/confirm_email/{confirmation_id}")
async def confirm_email_by_link(
    confirmation_id: str,
    db: Session = Depends(depends.get_db),
) -> Any:
    """
    Confirm the mail is correct or not and activate the account.
    """
    confirmation_email=users_utils.confirm_token(confirmation_id)
    user = crud.user.get_by_email(db, email=confirmation_email)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email doesn't exists in the system.",
        )
    
    user_in = {
        "is_active": True
    }
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

def init_app(app):
    app.include_router(router,prefix="/user")