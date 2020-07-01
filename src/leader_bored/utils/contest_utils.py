import httpx
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from leader_bored import crud, models, schemas

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

async def get_update_handles(db: Session, revert: bool, checkContest: models.Contests):
    finalHandles = []
    handles = crud.user.get_multi_handle(db)
    for handle in handles:
        toUpdate = await validate_user_addition(handle[0], db, checkContest, revert)
        if toUpdate:
            finalHandles.append(handle[0])

    return finalHandles 

async def validate_user_addition(
    handle: str,
    db:Session,
    checkContest: models.Contests,
    revert: bool
):
    user = crud.user.get_by_handle(db, handle=handle)
    if checkContest != None and revert == True and user.created_at > checkContest.added_at:
        return False
    elif checkContest != None and revert == False and checkContest.reverted_at != None and user.created_at > checkContest.reverted_at:
        return False

    return True

async def make_handle_string(handles: List[str])->str:
    separator = ';'
    return separator.join(handles)

async def get_cf_response(params: dict)->dict:
    async with httpx.AsyncClient() as client:
        response = await client.get('https://codeforces.com/api/contest.standings', params=params)
    return response.json()

async def calculate_cf_percentile(response: dict, revert: bool, totalParticipants: int):
    new_scores = {}
    response = response.get('rows', [])
    for entry in response:
        userHandle = entry.get('party', {}).get('members', [{}])[0].get('handle', '')
        new_scores[userHandle] = pow(-1, revert) * round((1 - entry.get('rank', totalParticipants) / totalParticipants), 4)
    return new_scores


async def update_databases(
    db:Session, 
    contestPercentile: dict,
    checkContest: models.Contests,
    contestId: int,
    contestName: str,
    contestType: str,
    contestDurationSeconds: int,
    contestStartTime: Optional[datetime],
    revert: bool
):
    for handle in contestPercentile:
        user = crud.user.get_by_handle(db, handle=handle)
        user_in = {'percent': contestPercentile.get(handle, 0)}
        crud.user.update(db, db_obj = user, obj_in = user_in)

    await modify_contest_db(checkContest, db,  contestId, contestName, contestType, 
            contestDurationSeconds, contestStartTime, revert)


async def modify_contest_db(
    checkContest: models.Contests,
    db: Session, 
    contestId: int,
    contestName: str, 
    contestType: str, 
    contestDurationSeconds: int,
    contestStartTime: Optional[datetime],
    revert: bool
):
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
