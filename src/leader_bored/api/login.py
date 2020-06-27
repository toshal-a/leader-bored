from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from leader_bored import crud, models, schemas
from leader_bored.core import depends, settings
from leader_bored.core.security import get_password_hash, create_access_token
from leader_bored.utils import users_utils

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(depends.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return schemas.Token(access_token=create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires), token_type="bearer")


@router.get("/confirm_email/{confirmation_id}")
async def confirm_email_by_link(
    confirmation_id: str,
    db: Session = Depends(depends.get_db),
) -> Any:
    """
    Confirm the mail is correct or not and activate the account.
    """
    confirmation_email = users_utils.confirm_token(confirmation_id)
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


@router.post("/reset_password")
async def forget_password(
    background_tasks: BackgroundTasks,
    user_in: schemas.UserEmail,
    db: Session = Depends(depends.get_db),
) -> Any:
    """
    Send link to email to reset password.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email does not exists in the system.",
        )

    background_tasks.add_task(
        users_utils.send_reset_password_email, user.email, user.handle)

    return {"msg": "Password recovery email sent"}


@router.get("/reset_password/{reset_id}")
async def reset_password(
    reset_id: str,
    user_in: schemas.UserUpdate,
    db: Session = Depends(depends.get_db),
) -> Any:
    """
    Change the password of a user after verifiying mail.
    """
    reset_email = users_utils.confirm_token(reset_id)
    user = crud.user.get_by_email(db, email=reset_email)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset link",
        )

    user_in = {
        "password": user_in.password
    }
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


def init_app(app):
    app.include_router(router, prefix="/login")
