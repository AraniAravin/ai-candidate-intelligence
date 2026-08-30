"""
evaluation.py
Ranking evaluation metrics: Precision@K, Recall@K, MRR, NDCG.
"""

import json
import math

from vector_store import search_candidates


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

def load_test_dataset(path: str = "data/test_dataset.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["test_cases"]


def get_actual_ranking(job_description: str, top_k: int = 5) -> list[str]:
    """Run the real system and return just the candidate names, in ranked order."""
    results = search_candidates(job_description, top_k=top_k)
    return [cid for cid, name, score, _ in results]  # unpack (id, name, score) from Day 19's updated signature


def evaluate_test_case(test_case: dict, k: int = 3) -> dict:
    """Run one test case through the real system and compute all four metrics."""
    expected = test_case["expected_ranking"]
    actual = get_actual_ranking(test_case["job_description"], top_k=max(k, len(expected)))

    return {
        "job_description": test_case["job_description"][:60] + "...",
        "expected": expected,
        "actual": actual,
        "precision_at_k": round(precision_at_k(actual, expected, k), 3),
        "recall_at_k": round(recall_at_k(actual, expected, k), 3),
        "mrr": round(reciprocal_rank(actual, expected), 3),
        "ndcg_at_k": round(ndcg_at_k(actual, expected, k), 3),
    }


def run_full_evaluation(k: int = 3) -> None:
    test_cases = load_test_dataset()
    all_results = []

    print(f"Running evaluation on {len(test_cases)} test case(s), K={k}\n")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, start=1):
        result = evaluate_test_case(test_case, k=k)
        all_results.append(result)

        print(f"\nTest Case {i}: {result['job_description']}")
        print(f"  Expected: {result['expected']}")
        print(f"  Actual:   {result['actual']}")
        print(f"  Precision@{k}: {result['precision_at_k']}")
        print(f"  Recall@{k}:    {result['recall_at_k']}")
        print(f"  MRR:           {result['mrr']}")
        print(f"  NDCG@{k}:      {result['ndcg_at_k']}")

    print("\n" + "=" * 60)
    print("AVERAGES ACROSS ALL TEST CASES")
    for metric in ["precision_at_k", "recall_at_k", "mrr", "ndcg_at_k"]:
        avg = sum(r[metric] for r in all_results) / len(all_results)
        print(f"  Mean {metric}: {avg:.3f}")


if __name__ == "__main__":
    run_full_evaluation(k=3)
    # # Worked example from Hour 1 — verify the functions match hand-calculated values
    # expected = ["Candidate 4", "Candidate 7", "Candidate 2"]
    # actual = ["Candidate 4", "Candidate 2", "Candidate 7"]

    # print(f"Precision@3: {precision_at_k(actual, expected, 3):.3f}  (expected 1.000)")
    # print(f"Recall@3:    {recall_at_k(actual, expected, 3):.3f}  (expected 1.000)")
    # print(f"MRR:         {reciprocal_rank(actual, expected):.3f}  (expected 1.000)")
    # print(f"NDCG@3:      {ndcg_at_k(actual, expected, 3):.3f}  (expected < 1.000, order differs)")