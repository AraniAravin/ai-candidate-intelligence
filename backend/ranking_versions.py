"""
ranking_versions.py
Three candidate-ranking approaches of increasing sophistication,
for comparison via MLflow experiment tracking.
"""

from sklearn.metrics.pairwise import cosine_similarity

from match import get_embedding


def semantic_score(job_embedding, candidate_cv_text: str) -> float:
    """Pure semantic similarity between job and candidate CV text."""
    candidate_embedding = get_embedding(candidate_cv_text)
    return float(cosine_similarity([job_embedding], [candidate_embedding])[0][0])


def skill_overlap_score(candidate_skills: list[str], required_skills: list[str]) -> float:
    """Fraction of required skills the candidate has (case-insensitive)."""
    if not required_skills:
        return 1.0
    candidate_set = {s.strip().lower() for s in candidate_skills}
    required_set = {s.strip().lower() for s in required_skills}
    overlap = candidate_set & required_set
    return len(overlap) / len(required_set)


def experience_match_score(candidate_years: int | None, required_years: int | None) -> float:
    """1.0 if candidate meets/exceeds required experience, partial credit otherwise."""
    if not required_years:
        return 1.0
    if candidate_years is None:
        return 0.0
    return min(candidate_years / required_years, 1.0)


def rank_v1_embedding_only(job_description: str, candidates: list[dict]) -> list[str]:
    """Version 1: pure semantic similarity."""
    job_embedding = get_embedding(job_description)
    scored = [(c["id"], semantic_score(job_embedding, c["cv_text"])) for c in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    #return [name for name, _ in scored]
    return [cid for cid, _ in scored]


def rank_v2_embedding_plus_skills(
    job_description: str, required_skills: list[str], candidates: list[dict],
    semantic_weight: float = 0.6, skill_weight: float = 0.4,
) -> list[str]:
    """Version 2: semantic similarity + skill overlap."""
    job_embedding = get_embedding(job_description)
    scored = []
    for c in candidates:
        s_score = semantic_score(job_embedding, c["cv_text"])
        k_score = skill_overlap_score(c["skills"], required_skills)
        composite = semantic_weight * s_score + skill_weight * k_score
        scored.append((c["id"], composite))
    scored.sort(key=lambda x: x[1], reverse=True)
    #return [name for name, _ in scored]
    return [cid for cid, _ in scored]


def rank_v3_full_composite(
    job_description: str, required_skills: list[str], experience_required: int | None,
    candidates: list[dict],
    semantic_weight: float = 0.5, skill_weight: float = 0.3, experience_weight: float = 0.2,
) -> list[str]:
    """Version 3: semantic similarity + skill overlap + experience match."""
    job_embedding = get_embedding(job_description)
    scored = []
    for c in candidates:
        s_score = semantic_score(job_embedding, c["cv_text"])
        k_score = skill_overlap_score(c["skills"], required_skills)
        e_score = experience_match_score(c["experience_years"], experience_required)
        composite = semantic_weight * s_score + skill_weight * k_score + experience_weight * e_score
        scored.append((c["id"], composite))
    scored.sort(key=lambda x: x[1], reverse=True)
    #return [name for name, _ in scored]
    return [cid for cid, _ in scored]