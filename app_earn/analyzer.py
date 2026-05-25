from collections import Counter
from typing import List


def compute_position_frequencies(arrays: List[List[int]]) -> List[List[tuple]]:
    results = []
    for arr in arrays:
        counter = Counter(arr)
        results.append(counter.most_common())
    return results


def get_top_n(ranked: List[tuple], n: int) -> List[tuple]:
    return ranked[:n]
