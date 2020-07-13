from typing import Any, Dict, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from leader_bored.crud.base import CRUDBase
from leader_bored.models.association import UserCodechef, UserCodeforces
from leader_bored.schemas.association import UserCodechefCreate, UserCodechefUpdate, UserCodeforcesCreate, UserCodeforcesUpdate

class CRUDUserCodeforces(CRUDBase[UserCodeforces, UserCodeforcesCreate, UserCodeforcesUpdate]):
    def get_by_primarykey(self, db: Session, user_id: int, contest_id: int) -> Optional[UserCodeforces]:
        return db.query(UserCodeforces).filter(and_(
            UserCodeforces.user_id == user_id,
            UserCodeforces.codeforces_id == contest_id
        )).first()

    def get_percentile(self, relation: UserCodeforces)-> Optional[float]:
        return relation.percentile

    def remove(self, db:Session, user_id: int, contest_id: int) -> Optional[UserCodeforces]:
        obj = self.get_by_primarykey(db, user_id, contest_id)
        db.delete(obj)
        db.commit()
        return obj 

class CRUDUserCodechef(CRUDBase[UserCodechef, UserCodechefCreate, UserCodechefUpdate]):
    def get_by_primarykey(self, db: Session, user_id: int, contest_id: str)-> Optional[UserCodechef]:
        return db.query(UserCodechef).filter(and_(
            UserCodechef.user_id.like(user_id),
            UserCodechef.codechef_id.like(contest_id)
        )).first()

    def get_percentile(self, relation: UserCodechef)-> Optional[float]: 
        return relation.percentile

user_codeforces = CRUDUserCodeforces(UserCodeforces)
user_codechef = CRUDUserCodechef(UserCodechef)