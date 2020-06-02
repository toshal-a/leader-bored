import httpx
from typing import List


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