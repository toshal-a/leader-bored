import httpx
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from leader_bored import crud, models, schemas

async def make_handle_string(handles: List[str])->str:
    separator = ';'
    handles = [x[0] for x in handles]
    return separator.join(handles)

async def get_cf_response(params: dict)->dict:
    async with httpx.AsyncClient() as client:
        response = await client.get('https://codeforces.com/api/contest.standings', params=params)
    return response.json()


async def calculate_cf_score(response: dict):
    new_scores = {}
    response = response.get('rows', [])
    for entry in response:
        userHandle = entry.get('party', {}).get('members', [{}])[0].get('handle', '')
        new_scores[userHandle] = entry.get('points', 0)

    return new_scores


async def calculate_icpc_score(response: dict):
    new_scores = {}
    ratings = []
    for problem in response.get('problems', []):
        ratings.append(problem.get('rating', 250) - 250)
    response = response.get('rows', [])
    for entry in response:
        userHandle = entry.get('party', {}).get('members', [{}])[0].get('handle', '')
        penalty = entry.get('penalty', 0)
        score = 0
        cnt = 0
        for problem in entry.get('problemResults', []):
            if problem.get("points", 0) == 1:
                score += ratings[cnt]
            cnt += 1
        score -= penalty
        score += (entry.get('successfulHackCount', 0) -
                  entry.get('unsuccessfulHackCount', 0)) * 10

        new_scores[userHandle] = score

    return new_scores

async def validate_contest_addition(
    checkContest: models.Contests,
    revert: bool,
    exception_obj: HTTPException
)->dict:
    if checkContest == None and revert == True:
        setattr(exception_obj, 'status_code', status.HTTP_405_METHOD_NOT_ALLOWED)
        setattr(
            exception_obj, 
            'detail',
            {
                "message": "The contest is not yet added. Please add the contest before reverting",
            }
        )
        raise exception_obj

    if revert == True and crud.contest.is_added(checkContest) == False:
        return {'message': "Contest is already reverted successfully not reverting once again"}
    if revert == False and checkContest != None and crud.contest.is_added(checkContest) == True:
        return {'message': "Contest is already added successfully not adding once again"}
    else:
        return {'message': 'Correct'}

async def update_user_score(
    user: models.Users,
    checkContest: models.Contests,
    db:Session,
    revert: bool,
    user_in: dict
):
    if checkContest != None and revert == True and user.created_at > checkContest.added_at:
        return
    elif checkContest != None and revert == False and checkContest.reverted_at != None and user.created_at > checkContest.reverted_at:
        return

    crud.user.update(db, db_obj=user, obj_in=user_in)

async def modify_contest_db(
    checkContest: models.Contests,
    db: Session, 
    contestId: int,
    contestName: str, 
    contestType: str, 
    contestDurationSeconds: int,
    contestStartTime: Optional[datetime],
    revert: bool):
    if checkContest == None:
        crud.contest.create(
            db, 
            obj_in= dict({
                'id': contestId,
                'contest_name' : contestName,
                'contest_type' : contestType,
                'duration_seconds': contestDurationSeconds,
                'starting_at' : contestStartTime
            })
        )
    else:
        if revert == True:
            crud.contest.update(
                db, db_obj=checkContest,
                obj_in  = dict({
                    'is_added':False,
                    'reverted_at' : datetime.utcnow(), 
                })
            )
        else:
            crud.contest.update(
                db, db_obj = checkContest,
                obj_in = dict({
                    'is_added': True,
                    'added_at': datetime.utcnow()
                })
            )