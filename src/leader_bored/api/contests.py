from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from leader_bored.utils import contest_utils
from leader_bored.core import depends
from leader_bored import crud, models, schemas

router = APIRouter()

@router.get("/{contest_id}", dependencies=[Depends(depends.verify_token)])
async def add_contest_score(contest_id: int, revert: bool = 0, db: Session = Depends(depends.get_db)):
    handles = crud.user.get_multi_handle(db)
    params = {
        'contestId': contest_id,
        'showUnofficial': 'false',
        'handles': await contest_utils.make_handle_string(handles)
    }
    response = await contest_utils.get_cf_response(params)

    if response.get( 'status', "") != 'OK':
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={
                "message": "There is an error fetching data from cf please try again after some time.",
                "api_response": response
            }
        )

    response = response.get('result', {})
    if response.get('contest', {}).get('phase', "") != 'FINISHED':
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail={
                "message": "The contest is not yet over. Please try again after some time",
                "contest_phase": response.get('contest', {}).get('phase', "")
            }
        )

    contestType = response.get('contest', {}).get('type', "")
    if contestType == 'CF' or contestType == 'IOI':
        contestScores = await contest_utils.calculate_cf_score(response)
    elif contestType == 'ICPC':
        contestScores = await contest_utils.calculate_icpc_score(response)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "This is a diffrent type of contest",
                "contest_type": contestType
            }
        )

    for handle in contestScores:
        user = crud.user.get_by_handle(db, handle=handle)
        if not user:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail="A user with given handle does not exist in data base.",
            )
        user_in = {'score': contestScores.get(handle, 0)}
        user = crud.user.update(db, db_obj=user, obj_in=user_in)

    return contestScores


def init_app(app):
    app.include_router(router, prefix="/contests")
