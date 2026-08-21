"""
evaluation.py
Ranking evaluation metrics: Precision@K, Recall@K, MRR, NDCG.
"""

import math


def precision_at_k(actual_ranking: list[str], expected_relevant: list[str], k: int) -> float:
    """Fraction of the top-K actual results that are in the expected relevant set."""
    top_k = actual_ranking[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for item in top_k if item in expected_relevant)
    return hits / len(top_k)


def recall_at_k(actual_ranking: list[str], expected_relevant: list[str], k: int) -> float:
    """Fraction of all expected relevant items captured in the top-K actual results."""
    if not expected_relevant:
        return 0.0
    top_k = actual_ranking[:k]
    hits = sum(1 for item in top_k if item in expected_relevant)
    return hits / len(expected_relevant)


def reciprocal_rank(actual_ranking: list[str], expected_relevant: list[str]) -> float:
    """1 / position of the first relevant item found (1-indexed). 0 if none found."""
    for i, item in enumerate(actual_ranking, start=1):
        if item in expected_relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(actual_ranking: list[str], expected_ranking: list[str], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain @ K.
    Uses binary relevance (1 if item is anywhere in expected_ranking, else 0),
    with an ideal ranking assumed to be expected_ranking's own order.
    """
    def dcg(ranking: list[str]) -> float:
        score = 0.0
        for i, item in enumerate(ranking[:k], start=1):
            relevance = 1.0 if item in expected_ranking else 0.0
            score += relevance / math.log2(i + 1)
        return score

    actual_dcg = dcg(actual_ranking)
    ideal_dcg = dcg(expected_ranking)  # the best possible ordering

    if ideal_dcg == 0:
        return 0.0
    return actual_dcg / ideal_dcg


if __name__ == "__main__":
    # Worked example from Hour 1 — verify the functions match hand-calculated values
    expected = ["Candidate 4", "Candidate 7", "Candidate 2"]
    actual = ["Candidate 4", "Candidate 2", "Candidate 7"]

    print(f"Precision@3: {precision_at_k(actual, expected, 3):.3f}  (expected 1.000)")
    print(f"Recall@3:    {recall_at_k(actual, expected, 3):.3f}  (expected 1.000)")
    print(f"MRR:         {reciprocal_rank(actual, expected):.3f}  (expected 1.000)")
    print(f"NDCG@3:      {ndcg_at_k(actual, expected, 3):.3f}  (expected < 1.000, order differs)")