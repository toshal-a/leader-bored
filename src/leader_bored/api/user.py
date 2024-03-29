from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
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

@router.get("/month", dependencies=[Depends(depends.verify_token)], response_model=List[schemas.UserInfoCodeforcesMonth])
async def get_month_users(
    month: int,
    year: int,
    db: Session = Depends(depends.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve users by month.
    """
    users = crud.user_codeforces_month.get_by_month(db, month, year)
    return users


@router.get("/top", response_model=List[schemas.User])
async def read_top_users(
    db: Session = Depends(depends.get_db),
    sortBy: str = None
) -> Any:
    """
    Retrieve top 10 users with sortBy param specified.
    """
    if sortBy is None:
        raise HTTPException(
            status_code=400,
            detail="SortBy parameter is not specified",
        )
    users = crud.user.get_multi_sortBy(db, skip=0, limit=10, sortBy=sortBy)
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
    return dict(handle=[getattr(handle, 'handle') for handle in handles])


@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: Session = Depends(depends.get_db),
    user_in: schemas.UserCreate,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )

    user = crud.user.get_by_handle(db, handle=user_in.handle)

    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with given handle exists.",
        )

    user = crud.user.create(db, obj_in=user_in)
    background_tasks.add_task(
        users_utils.send_new_account_email, user_in.email, user_in.handle)
    return user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: Session = Depends(depends.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.Users = Depends(depends.get_current_user),
) -> Any:
    """
    Update own user.
    """
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: models.Users = Depends(depends.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/me/month_stats", response_model=List[schemas.UserCodeforcesMonth])
async def read_user_month_stats(
    current_user: models.Users = Depends(depends.get_current_user),
    db: Session = Depends(depends.get_db)
):
    """
    Get information about the monthly statistics of logged in user.
    """
    return current_user.month_stats

@router.get("/me/codeforces_played", response_model=List[schemas.UserCodeforcesPlayed])
async def read_user_codeforces_contests(
    current_user: models.Users = Depends(depends.get_current_user),
    db: Session = Depends(depends.get_db)
):
    """
    Get information about all the contests played by logged in user.
    """
    codeforces_played = current_user.codeforces_played
    response = []

    for entry in codeforces_played: 
        cfContestId = entry.codeforces_id
        contest_detail = crud.codeforces_contest.get(db, cfContestId)
        response.append({
            "codeforces_id": cfContestId,
            "contest_name": contest_detail.contest_name,
            "contest_percentile": entry.percentile,
            "contest_time":  contest_detail.starting_at
        })
    
    return response


@router.get("/{user_id}", dependencies=[Depends(depends.verify_token)], response_model=schemas.User)
async def read_user_by_id(
    user_id: int,
    db: Session = Depends(depends.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    return user


@router.put("/{user_id}", dependencies=[Depends(depends.get_current_active_superuser)], response_model=schemas.User)
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
            detail="The user with this username does not exist in the system.",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", dependencies=[Depends(depends.get_current_active_superuser)], response_model=schemas.User)
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
    user = crud.user.remove(db, id=user_id)
    return user

@router.post("/feedback")
async def send_feedback(
    feedback_details: schemas.UserFeedback
) -> Any:
    """
    Post your feedback on the portal.
    """
    users_utils.send_feedback_mail(feedback_details.username, feedback_details.title, feedback_details.feedback)
    return {"status": 'OK'}


def init_app(app):
    app.include_router(router, prefix="/user")
