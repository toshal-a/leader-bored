import httpx
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from leader_bored import crud, models

async def validate_contest_addition(
    checkContest: models.Codeforces,
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

    if revert == True and checkContest.is_added == False:
        return {'message': "Contest is already reverted successfully not reverting once again"}
    if revert == False and checkContest != None and checkContest.is_added == True:
        return {'message': "Contest is already added successfully not adding once again"}
    else:
        return {'message': 'Correct'}

async def get_update_handles(db: Session, revert: bool, checkContest: models.Codeforces):
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
    checkContest: models.Codeforces,
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
    checkContest: models.Codeforces,
    contestId: int,
    contestPhase: str,
    contestName: str,
    contestType: str,
    contestDurationSeconds: int,
    contestStartTime: Optional[datetime],
    revert: bool
):
    await modify_contest_db(checkContest, db,  contestId, contestPhase, contestName, contestType, 
            contestDurationSeconds, contestStartTime, revert)

    for handle in contestPercentile:
        user = crud.user.get_by_handle(db, handle=handle)
        user_in = {'percent': contestPercentile.get(handle, 0)}
        crud.user.update(db, db_obj = user, obj_in = user_in)
        if contestPercentile.get(handle, 0) != 0: 
            if revert == False:
                relation_in = {
                    "user_id": user.id,
                    "codeforces_id": contestId,
                    'percentile': contestPercentile.get(handle, 0) 
                }
                relation_obj = crud.user_codeforces.create(db, relation_in)
            else: 
                crud.user_codeforces.remove(db, user.id, contestId)

async def modify_contest_db(
    checkContest: models.Codeforces,
    db: Session, 
    contestId: int,
    contestPhase: str,
    contestName: str, 
    contestType: str, 
    contestDurationSeconds: int,
    contestStartTime: Optional[datetime],
    revert: bool
):
    if checkContest == None:
        #crud.contest.create(
        #    db, 
        #    obj_in= dict({
        #        'id': contestId,
        #        'contest_name' : contestName,
        #        'contest_type' : contestType,
        #        'contest_status': contestPhase,
        #        'duration_seconds': contestDurationSeconds,
        #        'starting_at' : contestStartTime
        #    })
        #)

        crud.codeforces_contest.create(
            db,
            obj_in= dict({
                'id': contestId,
                'contest_name' : contestName,
                'contest_type' : contestType,
                'contest_status': contestPhase,
                'duration_seconds': contestDurationSeconds,
                'starting_at' : contestStartTime
            })
        )

    else:
        if revert == True:
            crud.codeforces_contest.update(
                db, db_obj=checkContest,
                obj_in  = dict({
                    'is_added':False,
                    'reverted_at' : datetime.utcnow(), 
                })
            )
        else:
            crud.codeforces_contest.update(
                db, db_obj = checkContest,
                obj_in = dict({
                    'is_added': True,
                    'added_at': datetime.utcnow()
                })
            )