from match import get_embedding, match_candidates


def test_embedding_has_correct_dimensions():
    embedding = get_embedding("Python backend developer")
    assert embedding.shape == (384,)


def test_similar_text_scores_higher_than_unrelated_text():
    job = "Python backend developer with FastAPI experience"
    candidates = {
        "Strong Match": "Developed REST APIs using Python and FastAPI",
        "Weak Match": "Experienced pastry chef with 10 years in baking",
    }

    results = match_candidates(job, candidates)

    assert results["Strong Match"] > results["Weak Match"]