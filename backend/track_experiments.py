"""
track_experiments.py
Runs all three ranking versions against the Day 22 test dataset,
logs parameters and metrics to MLflow for comparison.
"""

import mlflow

from database import SessionLocal
from models import Candidate, Job
from evaluation import (
    load_test_dataset, precision_at_k, recall_at_k, reciprocal_rank, ndcg_at_k,
)
from ranking_versions import rank_v1_embedding_only, rank_v2_embedding_plus_skills, rank_v3_full_composite

mlflow.set_experiment("candidate-ranking-approaches")


def load_candidates_for_eval(db) -> list[dict]:
    """Load all analyzed candidates with the fields ranking functions need."""
    candidates = db.query(Candidate).filter(Candidate.status == "analyzed").all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "cv_text": c.cv_text,
            "skills": [s.name for s in c.skills],
            "experience_years": c.experience_years,
        }
        for c in candidates
    ]


def evaluate_ranking(actual: list[str], expected: list[str], k: int = 3) -> dict:
    return {
        "precision_at_k": precision_at_k(actual, expected, k),
        "recall_at_k": recall_at_k(actual, expected, k),
        "mrr": reciprocal_rank(actual, expected),
        "ndcg_at_k": ndcg_at_k(actual, expected, k),
    }


def run_version(version_name: str, params: dict, ranking_fn, test_cases: list[dict], k: int = 3):
    """Run one ranking version across all test cases, log to MLflow."""
    with mlflow.start_run(run_name=version_name):
        mlflow.log_param("approach", version_name)
        for key, value in params.items():
            mlflow.log_param(key, value)

        all_metrics = []
        for test_case in test_cases:
            actual = ranking_fn(test_case)
            expected = test_case["expected_ranking"]
            print(f"DEBUG actual:   {actual}")
            print(f"DEBUG expected: {expected}")
            metrics = evaluate_ranking(actual, expected, k=k)
            all_metrics.append(metrics)

        for metric_name in ["precision_at_k", "recall_at_k", "mrr", "ndcg_at_k"]:
            mean_value = sum(m[metric_name] for m in all_metrics) / len(all_metrics)
            mlflow.log_metric(f"mean_{metric_name}", mean_value)
            print(f"  mean_{metric_name}: {mean_value:.3f}")


if __name__ == "__main__":
    db = SessionLocal()
    candidates = load_candidates_for_eval(db)
    test_cases = load_test_dataset()

    # Assumes each test case's job_description matches a real Job row for required_skills/experience.
    # For simplicity, look up job metadata by matching description text.
    jobs = db.query(Job).all()

    def find_job_for_case(test_case):
        return next((j for j in jobs if j.description.strip() == test_case["job_description"].strip()), None)

    print("Version 1: Embedding only")
    run_version(
        "v1_embedding_only",
        {},
        lambda tc: rank_v1_embedding_only(tc["job_description"], candidates),
        test_cases,
    )

    print("\nVersion 2: Embedding + Skills")
    def v2_fn(tc):
        job = find_job_for_case(tc)
        required_skills = job.required_skills.split(",") if job and job.required_skills else []
        return rank_v2_embedding_plus_skills(tc["job_description"], required_skills, candidates)

    run_version(
        "v2_embedding_plus_skills",
        {"semantic_weight": 0.6, "skill_weight": 0.4},
        v2_fn,
        test_cases,
    )

    print("\nVersion 3: Embedding + Skills + Experience")
    def v3_fn(tc):
        job = find_job_for_case(tc)
        required_skills = job.required_skills.split(",") if job and job.required_skills else []
        experience_required = job.experience_required if job else None
        return rank_v3_full_composite(
            tc["job_description"], required_skills, experience_required, candidates
        )

    run_version(
        "v3_embedding_skills_experience",
        {"semantic_weight": 0.5, "skill_weight": 0.3, "experience_weight": 0.2},
        v3_fn,
        test_cases,
    )

    db.close()
    print("\nDone. Run 'mlflow ui' and open http://127.0.0.1:5000 to compare runs.")