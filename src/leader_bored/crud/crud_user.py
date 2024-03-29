from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import desc

from leader_bored.core.security import get_password_hash, verify_password
from leader_bored.crud.base import CRUDBase
from leader_bored.models.user import Users
from leader_bored.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[Users, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Users]:
        return db.query(Users).filter(Users.email == email).first()

    def get_by_handle(self, db: Session, *, handle: str) -> Optional[Users]:
        return db.query(Users).filter(Users.handle == handle).first()

    def get_multi_sortBy(self, db: Session, *, skip: int = 0, limit: int = 10, sortBy: str) -> Optional[Users]:
        return db.query(Users).order_by(desc(getattr(Users, sortBy, 'avg_percent'))).offset(skip).limit(limit).all()

    def get_multi_handle(self, db: Session) -> Optional[Users]:
        return db.query(Users.handle).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> Users:
        db_obj = Users(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            handle=obj_in.handle,
            class_type=obj_in.class_type,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def getattribute(self, db_obj: Users, attr: str, defaultValue):
        return defaultValue if getattr(db_obj, attr, defaultValue) is None \
            else getattr(db_obj, attr)
        

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
        if "percent" in update_data:
            if update_data["percent"] != 0:
                update_data["aggr_percent"] = round(update_data["percent"] + \
                    self.getattribute(db_obj, "aggr_percent", 0), 4)
                if update_data["percent"] < 0:
                    update_data["contests_played"] = self.getattribute(
                        db_obj, "contests_played", 0) - 1
                else:
                    update_data["contests_played"] = 1 + \
                        self.getattribute(db_obj, "contests_played", 0)
                if update_data["contests_played"] == 0:
                    update_data["avg_percent"] = 0
                else:
                    update_data["avg_percent"] = round(update_data["aggr_percent"] / \
                        update_data["contests_played"], 4)
            del update_data["percent"]

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
