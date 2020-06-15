from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from leader_bored.core.security import get_password_hash, verify_password
from leader_bored.crud.base import CRUDBase
from leader_bored.models.user import Users
from leader_bored.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[Users, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Users]:
        return db.query(Users).filter(Users.email == email).first()

    def get_by_handle(self, db: Session, *, handle:str)-> Optional[Users]:
        return db.query(Users).filter(Users.handle == handle).first() 
    
    def get_multi_handle(self, db: Session) -> Optional[Users]:
        return db.query(Users.handle).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> Users:
        db_obj = Users(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            handle=obj_in.handle,
            class_type=obj_in.class_type,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Users, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> Users:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if "score" in update_data:
            update_data["overall_score"] = update_data["score"] + getattr(db_obj,"overall_score")
            del update_data["score"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[Users]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: Users) -> bool:
        return user.is_active

    def is_superuser(self, user: Users) -> bool:
        return user.is_superuser


user = CRUDUser(Users)
