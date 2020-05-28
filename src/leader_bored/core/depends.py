from typing import Generator, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer ,HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from leader_bored import crud, models, schemas
from leader_bored.core import security, settings
from leader_bored.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
    ) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenData(**payload)
    except (PyJWTError, ValidationError):
        raise credentials_exception
    user = crud.user.get(db,id=token_data.sub)
    if user is None:
        raise credentials_exception
    return user

async def verify_token(
    token : HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwt.decode(getattr(token,'credentials'), settings.SECRET_KEY, algorithms=[security.ALGORITHM])
    except (PyJWTError, ValidationError):
        raise credentials_exception
    return True


async def get_current_active_user(current_user: models.User = Depends(get_current_user)) ->models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(current_user: models.User = Depends(get_current_user)) ->models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user