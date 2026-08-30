"""
pipeline.py
End-to-end pipeline: Job Description + multiple CVs -> ranked candidates
by semantic similarity.
"""

from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

from match import get_embedding
from pdf_parser import extract_text_from_pdf


def rank_candidates(job_description: str, cv_paths: list[str]) -> list[tuple[str, float]]:
    """
    Rank candidate CVs against a job description using semantic similarity.

    Args:
        job_description: raw job description text
        cv_paths: list of paths to candidate CV PDF files

    Returns:
        list of (candidate_name, similarity_percentage) sorted highest first
    """
    job_embedding = get_embedding(job_description)

    results = []
    for cv_path in cv_paths:
        candidate_name = Path(cv_path).stem  # filename without extension, e.g. "cv_1"

        cv_text = extract_text_from_pdf(cv_path)
        cv_embedding = get_embedding(cv_text)

        similarity = cosine_similarity([job_embedding], [cv_embedding])[0][0]
        similarity_pct = round(float(similarity) * 100, 1)

        results.append((candidate_name, similarity_pct))

    # Sort by score, highest first
    results.sort(key=lambda x: x[1], reverse=True)
    return results


if __name__ == "__main__":
    job_description = """
    We are hiring a Python backend developer with experience building
        REST APIs using FastAPI. Experience with PostgreSQL and Docker
        is required.
    """

    cv_dir = Path("data/sample_cvs")
    cv_paths = [str(p) for p in cv_dir.glob("*.pdf")]

    if not cv_paths:
        print(f"No CVs found in {cv_dir}. Add sample CVs first.")
    else:
        print(f"Ranking {len(cv_paths)} candidates against the job description...\n")
        ranked = rank_candidates(job_description, cv_paths)

        print("Results:\n")
        for candidate_name, score in ranked:
            print(f"{candidate_name} — {score}%")