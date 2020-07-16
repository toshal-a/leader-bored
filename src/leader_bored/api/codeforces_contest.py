import copy
from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from leader_bored.utils import codeforces_contest_util
from leader_bored.core import depends
from leader_bored import crud, schemas

router = APIRouter()

@router.get("/add/{contest_id}", dependencies=[Depends(depends.verify_token)])
async def add_contest_score(
    contest_id: int, 
    background_tasks: BackgroundTasks,
    revert: bool = 0, 
    db: Session = Depends(depends.get_db),
):
    exception_obj = HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail=''
    )

    # Deepcopy to prevent cleaning of db object after commit.
    checkContest = crud.codeforces_contest.get(db, id = contest_id)
    if checkContest != None:
        checkContest = copy.deepcopy(checkContest)
    
    # Validate that we are not doing the same task again and again.
    validation_msg = await codeforces_contest_util.validate_contest_addition(checkContest, revert, exception_obj)
    if validation_msg.get('message', '') != 'Correct':
        return validation_msg

    # Get Handles whose percentile should be updated.
    handles = await codeforces_contest_util.get_update_handles(db, revert, checkContest)
    
    params = {
        'contestId': contest_id,
        'showUnofficial': 'false',
    }
    # Retrieve the information from cf api to calculate totalparticipants.
    response = await codeforces_contest_util.get_cf_response(params)
    if response.get( 'status', "") != 'OK':
        setattr(exception_obj, 'status_code', status.HTTP_424_FAILED_DEPENDENCY)
        setattr(
            exception_obj,
            'detail',
            {
                "message": "There is an error fetching data from cf for calculating total_participants please try again after some time.",
                "api_response": response
            }
        )
        raise exception_obj

    totalParticipants = len(response["result"]["rows"])

    if response.get('result', {}).get('contest', {}).get('phase', "") != 'FINISHED':
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

    params = {
        'contestId': contest_id,
        'showUnofficial': 'false',
        'handles': await codeforces_contest_util.make_handle_string(handles)
    }
    # Retrieve the information from cf api.
    response = await codeforces_contest_util.get_cf_response(params)

    # If the api call fails return response.
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

    # Information to be saved in contest table.
    contestType = response.get('contest', {}).get('type', "")
    contestName = response.get('contest', {}).get('name', "")
    contestId = response.get('contest', {}).get('id', 0)
    contestPhase = response.get('contest', {}).get('phase', "")
    contestDurationSeconds = response.get('contest', {}).get('durationSeconds', 0)
    contestStartTime = response.get('contest', {}).get('startTimeSeconds', None)
    if contestStartTime  != None:
        contestStartTime = datetime.utcfromtimestamp(contestStartTime).strftime('%Y-%m-%d %H:%M:%S') 
    
    # Calculate percentile for every individual according to contest type.
    contestPercentile = await codeforces_contest_util.calculate_cf_percentile(response, revert, totalParticipants)

    # Background task which will update the database in the backend after sending the response.
    background_tasks.add_task(codeforces_contest_util.update_databases, db, contestPercentile, checkContest, contestId,
            contestPhase, contestName, contestType, contestDurationSeconds, contestStartTime, revert)

    return contestPercentile

@router.get("/{contest_id}", dependencies=[Depends(depends.verify_token)], response_model= schemas.CodeforcesContest)
async def get_contest_info(contest_id: int, db: Session = Depends(depends.get_db)):
    """
    Get a specific contest by id.
    """
    contest = crud.codeforces_contest.get(db, id = contest_id)
    return contest

@router.get("/", dependencies=[Depends(depends.verify_token)], response_model = List[schemas.CodeforcesContest])
async def get_all_contests(skip: int=0, limit: int=100, db: Session = Depends(depends.get_db)):
    """
    Get information about all saved contests in database.
    """
    contests = crud.codeforces_contest.get_multi(db, skip = skip, limit = limit)
    return contests

@router.delete("/{contest_id}",dependencies=[Depends(depends.verify_token)], response_model=schemas.CodeforcesContest)
async def delete_contest(contest_id: int, db: Session = Depends(depends.get_db)) :
    """
    Delete a contest.
    """
    contest = crud.codeforces_contest.get(db, id=contest_id)
    if not contest:
        raise HTTPException(
            status_code=404,
            detail="The given contest is not added in to the database",
        )
    contest = crud.codeforces_contest.remove(db, id=contest_id)
    return contest

def init_app(app):
    app.include_router(router, prefix="/codeforces/contests")
