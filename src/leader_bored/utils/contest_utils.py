import httpx
from typing import List


async def make_handle_string(handles: List[str])->str:
    separator = ';'
    handles = [x[0] for x in handles]
    return separator.join(handles)

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