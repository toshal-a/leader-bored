from typing import Any, Dict, Optional, Union, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from leader_bored.crud.base import CRUDBase
from leader_bored.models import UserCodeforcesMonth
from leader_bored.schemas import UserCodeforcesMonthCreate, UserCodeforcesMonthUpdate, UserInfoCodeforcesMonth

class CRUDUserCodeforcesMonth(CRUDBase[UserCodeforcesMonth, UserCodeforcesMonthCreate, UserCodeforcesMonthUpdate]):
    def get_by_primarykey(self, db: Session, user_id: int, month: int, year: int) -> Optional[UserCodeforcesMonth]:
        return db.query(UserCodeforcesMonth).filter(and_(
            UserCodeforcesMonth.user_id == user_id,
            UserCodeforcesMonth.month == month,
            UserCodeforcesMonth.year == year
        )).first()

    def get_by_month(self, db: Session, month: int, year: int)-> List[UserInfoCodeforcesMonth]:
        monthInfoObjs = db.query(UserCodeforcesMonth).filter(and_(
            UserCodeforcesMonth.month == month,
            UserCodeforcesMonth.year == year,
        )).all()
        
        response = []
        for obj in monthInfoObjs:
            response.append({
                "email": obj.user.email,
                "full_name": obj.user.full_name,
                "handle" : obj.user.handle,
                "class_type": obj.user.class_type,
                "avg_percentile": obj.avg_percentile,
                "aggr_percentile": obj.aggr_percentile,
                "contests_played": obj.contests_played
            })
        return response

    def getattribute(self, db_obj: UserCodeforcesMonth, attr: str, defaultValue):
        return defaultValue if getattr(db_obj, attr, defaultValue) is None \
            else getattr(db_obj, attr)

    def update(
        self, db: Session, db_obj: UserCodeforcesMonth, obj_in: Union[UserCodeforcesMonthUpdate, Dict[str, Any]]
    ) -> UserCodeforcesMonth:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "percentile" in update_data:
            if update_data["percentile"] != 0:
                update_data["aggr_percentile"] = round(update_data["percentile"] + \
                    self.getattribute(db_obj, "aggr_percentile", 0), 4)
                if update_data["percentile"] < 0:
                    update_data["contests_played"] = self.getattribute(
                        db_obj, "contests_played", 0) - 1
                else:
                    update_data["contests_played"] = 1 + \
                        self.getattribute(db_obj, "contests_played", 0)
                if update_data["contests_played"] == 0:
                    update_data["avg_percentile"] = 0
                else:
                    update_data["avg_percentile"] = round(update_data["aggr_percentile"] / \
                        update_data["contests_played"], 4)
            del update_data["percentile"]

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove(self, db:Session, user_id: int, month: int, year: int) -> Optional[UserCodeforcesMonth]:
        obj = self.get_by_primarykey(db, user_id, month, year)
        db.delete(obj)
        db.commit()
        return obj 



user_codeforces_month = CRUDUserCodeforcesMonth(UserCodeforcesMonth)