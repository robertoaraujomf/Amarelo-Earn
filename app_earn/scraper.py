import requests
from typing import List, Dict


API_URL = "https://loteriascaixa-api.herokuapp.com/api/megasena"


def fetch_all_results() -> List[Dict]:
    resp = requests.get(API_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        raise ValueError(f"Unexpected API response format: expected list, got {type(data).__name__}")

    return data


def extract_draws(data: List[Dict]) -> List[List[int]]:
    draws = []
    for contest in data:
        dezenas = contest.get("dezenasOrdemSorteio") or contest.get("dezenas")
        if dezenas and isinstance(dezenas, list):
            draw = [int(d) for d in dezenas if d]
            if len(draw) == 6:
                draws.append(draw)
    return draws


def split_by_position(draws: List[List[int]]) -> List[List[int]]:
    positions = [[], [], [], [], [], []]
    for draw in draws:
        for i in range(6):
            positions[i].append(draw[i])
    return positions
