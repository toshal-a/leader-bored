from typing import Any, Dict, Optional, Union
from datetime import datetime

from sqlalchemy.orm import Session

from leader_bored.crud.base import CRUDBase
from leader_bored.models.contests import Contests
from leader_bored.schemas.contests import ContestCreate, ContestUpdate


class CRUDContest(CRUDBase[Contests, ContestCreate, ContestUpdate]):
    def get_addition_time(self, contest: Contests)-> Optional[datetime]:
        return contest.added_at
    
    def get_reverted_time(self, contest: Contests)->Optional[datetime]:
        return contest.reverted_at

    def is_added(self, contest: Contests) -> bool:
        return contest.is_added

contest = CRUDContest(Contests)