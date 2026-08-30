


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job_with_mocked_extraction(client, monkeypatch):
    fake_profile = {
        "role": "AI Engineer",
        "required_skills": ["Python", "Docker"],
        "nice_to_have_skills": ["FastAPI"],
        "experience_required": 2,
    }

    import main
    monkeypatch.setattr(main, "extract_job_info", lambda description: fake_profile)

    response = client.post("/jobs", json={"description": "We need an AI Engineer..."})

    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "AI Engineer"
    assert "Python" in data["required_skills"]


def test_create_job_rejects_missing_description(client):
    response = client.post("/jobs", json={})
    assert response.status_code == 422  # Pydantic validation error


def test_get_nonexistent_job_returns_404(client):
    response = client.get("/jobs/9999/ranked-candidates")
    assert response.status_code == 404


def test_delete_nonexistent_candidate_returns_404(client):
    response = client.delete("/candidates/9999")
    assert response.status_code == 404


# def test_analyze_handles_extraction_failure_gracefully(client, monkeypatch):
#     """
#     Simulates a broken PDF: extract_text_from_pdf raises an error.
#     The endpoint should mark the candidate 'failed', not crash.
#     """
#     import main
#     from models import Candidate

#     # Insert a fake 'uploaded' candidate directly into the test DB
#     db_gen = main.get_db()
#     db = next(db_gen)
#     candidate = Candidate(name=None, cv_path="fake/path.pdf", status="uploaded")
#     db.add(candidate)
#     db.commit()

#     def broken_extract(path):
#         raise ValueError("Corrupt PDF")

#     monkeypatch.setattr(main, "extract_text_from_pdf", broken_extract)

#     response = client.post("/candidates/analyze")

#     assert response.status_code == 200
#     data = response.json()
#     assert len(data["failed"]) == 1
#     assert data["failed"][0]["reason"] == "Corrupt PDF"

def test_analyze_handles_extraction_failure_gracefully(client, test_db, monkeypatch):
    """
    Simulates a broken PDF: extract_text_from_pdf raises an error.
    The endpoint should mark the candidate 'failed', not crash.
    """
    import main
    from models import Candidate

    # Insert a fake 'uploaded' candidate directly into the test DB
    candidate = Candidate(name=None, cv_path="fake/path.pdf", status="uploaded")
    test_db.add(candidate)
    test_db.commit()

    def broken_extract(path):
        raise ValueError("Corrupt PDF")

    monkeypatch.setattr(main, "extract_text_from_pdf", broken_extract)

    response = client.post("/candidates/analyze")

    assert response.status_code == 200
    data = response.json()
    assert len(data["failed"]) == 1