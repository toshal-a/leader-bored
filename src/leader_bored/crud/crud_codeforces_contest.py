from typing import Any, Dict, Optional, Union
from datetime import datetime

from sqlalchemy.orm import Session

from leader_bored.crud.base import CRUDBase
from leader_bored.models.codeforces_contest import Codeforces
from leader_bored.schemas.codeforces_contest import CodeforcesContestCreate, CodeforcesContestUpdate

codeforces_contest = CRUDBase[Codeforces, CodeforcesContestCreate, CodeforcesContestUpdate](Codeforces)