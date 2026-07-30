"""
match.py
Compares a job description against multiple candidate CV texts
using sentence embeddings and cosine similarity.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the pretrained embedding model once, reused for every comparison
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


def get_embedding(text: str):
    """Convert a piece of text into its embedding vector."""
    return model.encode(text)


def match_candidates(job_description: str, candidates: dict[str, str]) -> dict[str, float]:
    """
    Compare a job description against multiple candidates.

    Args:
        job_description: the job description text
        candidates: dict mapping candidate name -> CV text

    Returns:
        dict mapping candidate name -> similarity score, sorted highest first
    """
    job_embedding = get_embedding(job_description)
    print(job_embedding.shape)

    scores = {}
    for name, cv_text in candidates.items():
        cv_embedding = get_embedding(cv_text)
        similarity = cosine_similarity([job_embedding], [cv_embedding])[0][0]
        scores[name] = round(float(similarity), 4)

    # Sort by score, highest first
    ranked = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return ranked


if __name__ == "__main__":
    job_description = "Python backend developer with FastAPI experience"

    candidates = {
        "Candidate A": "Developed REST APIs using Python and FastAPI for 3 years",
        "Candidate B": "Backend engineer skilled in Python, Django, and PostgreSQL",
        "Candidate C": "Frontend developer specializing in React and CSS",
    }

    results = match_candidates(job_description, candidates)

    print(f"\nJob Description: {job_description}\n")
    print("Ranked Candidates:")
    for name, score in results.items():
        print(f"{name} -> {score}")