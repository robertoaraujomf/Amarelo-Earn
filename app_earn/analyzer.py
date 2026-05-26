from collections import Counter
from typing import List


def compute_position_frequencies(arrays: List[List[int]]) -> List[List[tuple]]:
    results = []
    for arr in arrays:
        counter = Counter(arr)
        full = []
        for n in range(1, 61):
            full.append((n, counter.get(n, 0)))
        full.sort(key=lambda x: (-x[1], x[0]))
        results.append(full)
    return results


def get_top_n(ranked: List[tuple], n: int) -> List[tuple]:
    return ranked[:n]
