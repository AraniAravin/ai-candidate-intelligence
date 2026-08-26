"""
main.py
FastAPI application wiring together the AI pipeline built in Weeks 1-2.
"""

from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil


from database import get_db, engine, Base
import models  # noqa: F401
import crud

from pdf_parser import extract_text_from_pdf
from extract_job_info import extract_job_info
from extract_candidate_info import extract_candidate_info
from vector_store import (
    create_collection,
    insert_candidate,
    search_candidates,
    delete_candidate as delete_candidate_from_qdrant,
    reset_collection as reset_qdrant_collection,
)
from rag_chat import explain_ranking,answer_recruiter_question

app = FastAPI(title="AI Candidate Intelligence Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the Qdrant collection exists when the app starts
create_collection()
Base.metadata.create_all(bind=engine)  # safe no-op if tables already exist

UPLOAD_DIR = Path("data/uploaded_cvs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory storage for now — real DB (PostgreSQL) comes later.
# This is a deliberate, temporary simplification.
#jobs_db: dict[int, dict] = {}
#next_job_id = 1

# candidates_db: dict[int, dict] = {}
# next_candidate_id = 1

class CandidateResponse(BaseModel):
    id: int
    name: str | None
    status: str
    skills: list[str] = []
    experience_years: int | None = None
    education: str | None = None

    class Config:
        from_attributes = True




# ---------- Pydantic models: define request/response shapes ----------

class JobCreateRequest(BaseModel):
    description: str


class JobResponse(BaseModel):
    id: int
    description: str
    role: str | None
    required_skills: list[str]
    nice_to_have_skills: list[str]
    experience_required: int | None


class ChatRequest(BaseModel):
    question: str
    job_id: int | None = None


class ChatResponse(BaseModel):
    answer: str
class RankedCandidate(BaseModel):
    id:int
    name: str
    score: float

class RankingResponse(BaseModel):
    job_id: int
    ranked_candidates: list[RankedCandidate]

# ---------- Endpoints ----------

@app.get("/health")
def health_check():
    """Simple liveness check — no body needed, just confirms the API is up."""
    return {"status": "ok"}

@app.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreateRequest, db: Session = Depends(get_db)):
    """Create a job posting and extract its structured profile via LLM, persist to PostgreSQL."""

    profile = extract_job_info(job.description)

    job_record = crud.create_job(db, description=job.description, profile=profile)
    skills = crud.job_skills_as_list(job_record)

    return JobResponse(
        id=job_record.id,
        description=job_record.description,
        role=job_record.role,
        required_skills=skills["required_skills"],
        nice_to_have_skills=skills["nice_to_have_skills"],
        experience_required=job_record.experience_required,
    )

@app.get("/jobs", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """Return all persisted jobs."""
    jobs = crud.get_all_jobs(db)
    responses = []
    for job in jobs:
        skills = crud.job_skills_as_list(job)
        responses.append(JobResponse(
            id=job.id,
            description=job.description,
            role=job.role,
            required_skills=skills["required_skills"],
            nice_to_have_skills=skills["nice_to_have_skills"],
            experience_required=job.experience_required,
        ))
    return responses


@app.post("/candidates/upload")
async def upload_candidates(files: list[UploadFile] = File(...),db: Session = Depends(get_db),):
    """Upload one or more CV PDFs, save them to disk."""
    #global next_candidate_id
    saved = []

    for file in files:
        dest_path = UPLOAD_DIR / file.filename
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # candidates_db[next_candidate_id] = {
        #     "id": next_candidate_id,
        #     "filename": file.filename,
        #     "path": str(dest_path),
        #     "status": "uploaded",
        # }
        candidate = crud.create_candidate(db, filename=file.filename, cv_path=str(dest_path))
        saved.append({"id": candidate.id, "filename": file.filename})
        #next_candidate_id += 1

    return {"uploaded": saved}


# @app.post("/candidates/analyze")
# def analyze_candidates():
#     """
#     Process all uploaded-but-not-yet-analyzed candidates:
#     extract text, extract structured info, embed, and store in Qdrant.
#     """
#     processed = []

#     for candidate_id, record in candidates_db.items():
#         if record["status"] != "uploaded":
#             continue

#         cv_text = extract_text_from_pdf(record["path"])
#         info = extract_candidate_info(cv_text)

#         insert_candidate(
#             point_id=candidate_id,
#             name=info.get("name") or record["filename"],
#             cv_text=cv_text,
#         )

#         record["status"] = "analyzed"
#         record["extracted_info"] = info
#         processed.append({"id": candidate_id, "info": info})

#     return {"processed": processed}
@app.post("/candidates/analyze")
def analyze_candidates(db: Session = Depends(get_db)):
    processed = []
    failed = []

    candidates = db.query(models.Candidate).filter(or_(models.Candidate.status == "uploaded",
            models.Candidate.status == "failed",
        )).all()

    for candidate in candidates:

        try:
            cv_text = extract_text_from_pdf(candidate.cv_path)
            if not cv_text.strip():
                raise ValueError("Extracted text is empty (possibly a scanned/image PDF)")
            info = extract_candidate_info(cv_text)

            candidate = crud.save_extracted_info(db, candidate, cv_text, info)

            insert_candidate(
                point_id=candidate.id,
                name=candidate.name or Path(candidate.cv_path).stem,
                cv_text=cv_text,
            )

            processed.append({"id": candidate.id, "name": candidate.name})

        except Exception as e:
            crud.mark_candidate_failed(db, candidate, str(e))
            failed.append({"id": candidate.id, "reason": str(e)})

    return {"processed": processed, "failed": failed}

@app.get("/candidates", response_model=list[CandidateResponse])
def list_candidates(db: Session = Depends(get_db)):
    """Return all candidates with their persisted extracted info."""
    candidates = crud.get_all_candidates(db)
    return [
        CandidateResponse(
            id=c.id,
            name=c.name,
            status=c.status,
            skills=[s.name for s in c.skills],
            experience_years=c.experience_years,
            education=c.education,
        )
        for c in candidates
    ]


@app.get("/jobs/{job_id}/ranked-candidates", response_model=RankingResponse)
def rank_candidates_for_job(job_id: int, top_k: int = 5,db: Session = Depends(get_db)):
    """
    Rank analyzed candidates against a job description using
    semantic similarity search in Qdrant.
    """
    job = crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    

    results = search_candidates(job.description, top_k=top_k)
    ranked = [{"id": cid,"name": name, "score": score,"cv_text":cv_text} for cid,name, score,cv_text in results]

    return {"job_id": job_id, "ranked_candidates": ranked}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    General AI recruitment assistant. Can answer comparison questions
    ("why is A better than B?") and filtering questions
    ("which candidates know Python and AWS?") using all analyzed candidates.
    """
    job_description = ""
    if request.job_id is not None:
        job = crud.get_job(db, request.job_id)
        if job:
            job_description = job.description

    all_candidates = crud.get_all_candidates(db)
    candidates_data = [
        {
            "name": c.name,
            "skills": [s.name for s in c.skills],
            "experience_years": c.experience_years,
            "education": c.education,
        }
        for c in all_candidates
        if c.status == "analyzed"
    ]

    answer = answer_recruiter_question(request.question, job_description, candidates_data)
    return {"answer": answer}

@app.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate_detail(candidate_id: int, db: Session = Depends(get_db)):
    """Return full details for a single candidate."""
    candidate = crud.get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    return CandidateResponse(
        id=candidate.id,
        name=candidate.name,
        status=candidate.status,
        skills=[s.name for s in candidate.skills],
        experience_years=candidate.experience_years,
        education=candidate.education,
    )

class MatchDetailResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    job_id: int
    score: float
    matching_skills: list[str]
    missing_skills: list[str]
    experience_years: int | None
    explanation: str


@app.get("/jobs/{job_id}/candidates/{candidate_id}/match-details", response_model=MatchDetailResponse)
def get_match_details(job_id: int, candidate_id: int, db: Session = Depends(get_db)):
    """Full match breakdown for one candidate against one job:
    semantic score, matching/missing skills, and an AI-generated explanation."""
    job = crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    candidate = crud.get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    # Semantic score: reuse the same search results this candidate would appear in
    results = search_candidates(job.description, top_k=1000)
    score = next((s for cid, name, s,cv_text in results if cid == candidate_id), 0.0)

    job_skills = crud.job_skills_as_list(job)
    skill_match = crud.compute_skill_match(
        candidate_skills=[s.name for s in candidate.skills],
        required_skills=job_skills["required_skills"],
    )

    explanation = explain_ranking(candidate.name, job.description)

    return MatchDetailResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        job_id=job.id,
        score=round(score * 100, 1),
        matching_skills=skill_match["matching_skills"],
        missing_skills=skill_match["missing_skills"],
        experience_years=candidate.experience_years,
        explanation=explanation,
    )

## Delete and resets 
@app.delete("/candidates/{candidate_id}")
def remove_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate from both PostgreSQL and Qdrant."""
    deleted = crud.delete_candidate(db, candidate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    delete_candidate_from_qdrant(candidate_id)  # renamed import, see note below
    return {"deleted": candidate_id}


@app.delete("/jobs/{job_id}")
def remove_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job from PostgreSQL."""
    deleted = crud.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"deleted": job_id}


@app.post("/admin/reset/candidates")
def reset_candidates(confirm: bool = False, db: Session = Depends(get_db)):
    """Wipe ALL candidates from Postgres and Qdrant, restart IDs at 1.
    Requires confirm=true to actually run — this is destructive and irreversible."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Pass confirm=true to proceed. This permanently deletes all candidate data.")

    crud.reset_candidates_table(db)
    reset_qdrant_collection()
    return {"status": "candidates reset — IDs will restart at 1"}


@app.post("/admin/reset/jobs")
def reset_jobs(confirm: bool = False, db: Session = Depends(get_db)):
    """Wipe ALL jobs from Postgres, restart IDs at 1."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Pass confirm=true to proceed. This permanently deletes all job data.")

    crud.reset_jobs_table(db)
    return {"status": "jobs reset — IDs will restart at 1"}


@app.post("/admin/reset/all")
def reset_all(confirm: bool = False, db: Session = Depends(get_db)):
    """Wipe ALL candidates and jobs from both databases, restart both ID sequences at 1."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Pass confirm=true to proceed. This permanently deletes all data.")

    crud.reset_candidates_table(db)
    crud.reset_jobs_table(db)
    reset_qdrant_collection()
    return {"status": "candidates and jobs fully reset — all IDs will restart at 1"}