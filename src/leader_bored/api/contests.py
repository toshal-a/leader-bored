import copy
from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from leader_bored.utils import contest_utils
from leader_bored.core import depends
from leader_bored import crud, models, schemas

router = APIRouter()

@router.get("/add/{contest_id}", dependencies=[Depends(depends.verify_token)])
async def add_contest_score(contest_id: int, revert: bool = 0, db: Session = Depends(depends.get_db)):
    exception_obj = HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail=''
    )

    checkContest = crud.contest.get(db, id = contest_id)
    if checkContest != None:
        checkContest = copy.deepcopy(checkContest)
    
    validation_msg = await contest_utils.validate_contest_addition(checkContest, revert, exception_obj)
    if validation_msg.get('message', '') != 'Correct':
        return validation_msg

    handles = crud.user.get_multi_handle(db)
    
    params = {
        'contestId': contest_id,
        'showUnofficial': 'false',
        'handles': await contest_utils.make_handle_string(handles)
    }
    response = await contest_utils.get_cf_response(params)

    if response.get( 'status', "") != 'OK':
        setattr(exception_obj, 'status_code', status.HTTP_424_FAILED_DEPENDENCY)
        setattr(
            exception_obj,
            'detail',
            {
                "message": "There is an error fetching data from cf please try again after some time.",
                "api_response": response
            }
        )
        raise exception_obj

    response = response.get('result', {})
    if response.get('contest', {}).get('phase', "") != 'FINISHED':
        setattr(exception_obj, 'status_code', status.HTTP_405_METHOD_NOT_ALLOWED)
        setattr(
            exception_obj, 
            'detail',
            {
                "message": "The contest is not yet over. Please try again after some time",
                "contest_phase": response.get('contest', {}).get('phase', "")
            }
        )
        raise exception_obj

    contestType = response.get('contest', {}).get('type', "")
    contestName = response.get('contest', {}).get('name', "")
    contestId = response.get('contest', {}).get('id', 0)
    contestDurationSeconds = response.get('contest', {}).get('durationSeconds', 0)
    contestStartTime = response.get('contest', {}).get('startTimeSeconds', None)
    if contestStartTime  != None:
        contestStartTime = datetime.utcfromtimestamp(contestStartTime).strftime('%Y-%m-%d %H:%M:%S') 
    
    if contestType == 'CF' or contestType == 'IOI':
        contestScores = await contest_utils.calculate_cf_score(response)
    elif contestType == 'ICPC':
        contestScores = await contest_utils.calculate_icpc_score(response)
    else:
        setattr(exception_obj, 'status_code', status.HTTP_400_BAD_REQUEST)
        setattr(
            exception_obj,
            'detail',
            {
                "message": "This is a diffrent type of contest",
                "contest_type": contestType
            } 
        )
        raise exception_obj

    for handle in contestScores:
        user = crud.user.get_by_handle(db, handle=handle)
        if not user:
            setattr(exception_obj, 'status_code', status.HTTP_409_CONFLICT)
            setattr(
                exception_obj,
                'detail',
                {
                    'message': "A user with given handle %s does not exist in data base." % (handle),
                    'reverted' : revert 
                }
            )
            raise exception_obj
        user_in = {'score': contestScores.get(handle, 0)}
        if revert == 1:
            user_in['score'] *= (-1)
            if checkContest != None and user.created_at > checkContest.added_at:
                continue
        elif checkContest != None and revert == 0 and checkContest.reverted_at != None and user.created_at > checkContest.reverted_at:
            continue

        crud.user.update(db, db_obj=user, obj_in=user_in)
 
    await contest_utils.modify_contest_db(checkContest, db,  contestId, contestName, contestType, 
            contestDurationSeconds, contestStartTime, revert)

    return contestScores

@router.get("/{contest_id}", dependencies=[Depends(depends.verify_token)], response_model= schemas.Contest)
async def get_contest_info(contest_id: int, db: Session = Depends(depends.get_db)):
    """
    Get a specific contest by id.
    """
    contest = crud.contest.get(db, id = contest_id)
    return contest

@router.get("/", dependencies=[Depends(depends.verify_token)], response_model = List[schemas.Contest])
async def get_all_contests(skip: int=0, limit: int=100, db: Session = Depends(depends.get_db)):
    """
    Get information about all saved contests in database.
    """
    contests = crud.contest.get_multi(db, skip = skip, limit = limit)
    return contests

@router.delete("/{contest_id}",dependencies=[Depends(depends.verify_token)], response_model=schemas.Contest)
async def delete_contest(contest_id: int, db: Session = Depends(depends.get_db)) :
    """
    Delete a contest.
    """
    contest = crud.contest.get(db, id=contest_id)
    if not contest:
        raise HTTPException(
            status_code=404,
            detail="The given contest is not added in to the database",
        )
    contest = crud.contest.remove(db, id=contest_id)
    return contest

def init_app(app):
    app.include_router(router, prefix="/contests")
