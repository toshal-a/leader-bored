from fastapi import APIRouter, Body, Depends, HTTPException
import httpx
from sqlalchemy.orm import Session
from typing import List

from leader_bored.core import depends
from leader_bored import crud, models, schemas

router = APIRouter()


async def make_handle_string(handles: List[str]):
    stringHandle = ""
    for handle in handles:
        stringHandle += handle[0]
        stringHandle += ';'
    return stringHandle


async def get_cf_response(params: dict):
    async with httpx.AsyncClient() as client:
        response = await client.get('https://codeforces.com/api/contest.standings', params=params)
    #response = {}
    return response.json()


async def calculate_cf_score(response: dict):
    new_scores = {}
    response = response['rows']
    for entry in response:
        userHandle = entry['party']['members'][0]['handle']
        new_scores[userHandle] = entry['points']

    return new_scores


async def calculate_icpc_score(response: dict):
    new_scores = {}
    ratings = []
    for problem in response['problems']:
        ratings.append(problem['rating'] - 250)
    response = response['rows']
    for entry in response:
        userHandle = entry['party']['members'][0]['handle']
        penalty = entry['penalty']
        score = 0
        cnt = 0
        for problem in entry['problemResults']:
            if problem["points"] == 1:
                score += ratings[cnt]
            cnt += 1
        score -= penalty
        score += (entry['successfulHackCount'] -
                  entry['unsuccessfulHackCount']) * 10

        new_scores[userHandle] = score

    return new_scores


@router.get("/{contest_id}", dependencies=[Depends(depends.verify_token)])
async def add_contest_score(contest_id: int, db: Session = Depends(depends.get_db)):
    handles = crud.user.get_multi_handle(db)
    params = {
        'contestId': contest_id,
        'showUnofficial': 'false',
        'handles': await make_handle_string(handles)
    }
    response = await get_cf_response(params)

    if response['status'] != 'OK':
        raise HTTPException(
            status_code=404,
            detail={
                "message": "There is an error fetching data from cf please try again after some time.",
                "api_response": response
            }
        )

    response = response['result']
    if response['contest']['phase'] != 'FINISHED':
        raise HTTPException(
            status_code=404,
            detail={
                "message": "The contest is not yet over. Please try again after some time",
                "contest_phase": response['contest']['phase']
            }
        )

    if response['contest']['type'] == 'CF' or response['contest']['type'] == 'IOI':
        contestScores = await calculate_cf_score(response)
    elif response['contest']['type'] == 'ICPC':
        contestScores = await calculate_icpc_score(response)
    else:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "This is a diffrent type of contest",
                "contest_type": response['contest']['type']
            }
        )

    for handle in contestScores:
        user = crud.user.get_by_handle(db, handle=handle)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="A user with given handle does not exist in data base.",
            )
        user_in = {'score': contestScores[handle]}
        user = crud.user.update(db, db_obj=user, obj_in=user_in)

    return contestScores


def init_app(app):
    app.include_router(router, prefix="/contests")
