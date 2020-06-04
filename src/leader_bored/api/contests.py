import copy
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from leader_bored.utils import contest_utils
from leader_bored.core import depends
from leader_bored import crud, models, schemas

router = APIRouter()

@router.get("/{contest_id}", dependencies=[Depends(depends.verify_token)])
async def add_contest_score(contest_id: int, revert: bool = 0, db: Session = Depends(depends.get_db)):
    exception_obj = HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail=''
    )

    checkContest = crud.contest.get(db, id = contest_id)
    if checkContest != None:
        checkContest = copy.deepcopy(checkContest)
    
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

    return contestScores


def init_app(app):
    app.include_router(router, prefix="/contests")
