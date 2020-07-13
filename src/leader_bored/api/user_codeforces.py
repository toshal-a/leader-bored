from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from leader_bored import crud, models, schemas
from leader_bored.core import depends, settings
from leader_bored.utils import users_utils

router = APIRouter()


@router.get("/", dependencies=[Depends(depends.verify_token)], response_model=List[schemas.UserCodeforcesCreate])
async def read_user_codeforces_relations(
    db: Session = Depends(depends.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve users and contest relations.
    """
    relations = crud.user_codeforces.get_multi(db, skip=skip, limit=limit)
    return relations

def init_app(app):
    app.include_router(router, prefix="/user_codeforces")
