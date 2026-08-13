"""
main.py
FastAPI application wiring together the AI pipeline built in Weeks 1-2.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil

from pdf_parser import extract_text_from_pdf
from extract_job_info import extract_job_info
from extract_candidate_info import extract_candidate_info
from vector_store import create_collection, insert_candidate, search_candidates
from rag_chat import explain_ranking

app = FastAPI(title="AI Candidate Intelligence Platform")

# Ensure the Qdrant collection exists when the app starts
create_collection()

UPLOAD_DIR = Path("data/uploaded_cvs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory storage for now — real DB (PostgreSQL) comes later.
# This is a deliberate, temporary simplification.
jobs_db: dict[int, dict] = {}
next_job_id = 1

candidates_db: dict[int, dict] = {}
next_candidate_id = 1


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
    candidate_name: str
    job_description: str


class ChatResponse(BaseModel):
    answer: str
class RankedCandidate(BaseModel):
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
def create_job(job: JobCreateRequest):
    """Create a job posting and extract its structured profile."""
    global next_job_id

    profile = extract_job_info(job.description)

    job_record = {
        "id": next_job_id,
        "description": job.description,
        "role": profile.get("role"),
        "required_skills": profile.get("required_skills", []),
        "nice_to_have_skills": profile.get("nice_to_have_skills", []),
        "experience_required": profile.get("experience_required"),
    }
    jobs_db[next_job_id] = job_record
    next_job_id += 1

    return job_record


@app.post("/candidates/upload")
async def upload_candidates(files: list[UploadFile] = File(...)):
    """Upload one or more CV PDFs, save them to disk."""
    global next_candidate_id
    saved = []

    for file in files:
        dest_path = UPLOAD_DIR / file.filename
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        candidates_db[next_candidate_id] = {
            "id": next_candidate_id,
            "filename": file.filename,
            "path": str(dest_path),
            "status": "uploaded",
        }
        saved.append({"id": next_candidate_id, "filename": file.filename})
        next_candidate_id += 1

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
def analyze_candidates():
    processed = []
    failed = []

    for candidate_id, record in candidates_db.items():
        if record["status"] != "uploaded":
            continue
        record["status"] = "processing"

        try:
            cv_text = extract_text_from_pdf(record["path"])
            if not cv_text.strip():
                raise ValueError("Extracted text is empty (possibly a scanned/image PDF)")
            info = extract_candidate_info(cv_text)

            insert_candidate(
                point_id=candidate_id,
                name=info.get("name") or record["filename"],
                cv_text=cv_text,
            )

            record["status"] = "analyzed"
            record["extracted_info"] = info
            processed.append({"id": candidate_id, "info": info})

        except Exception as e:
            record["status"] = "failed"
            record["failure_reason"] = str(e)
            failed.append({"id": candidate_id, "filename": record["filename"], "reason": str(e)})

    return {"processed": processed, "failed": failed}

@app.get("/candidates/status")
def get_candidates_status():
    """Return the current status of every uploaded candidate — useful for
    checking processing progress without re-running analyze."""
    return {
        "candidates": [
            {
                "id": cid,
                "filename": record["filename"],
                "status": record["status"],
                "failure_reason": record.get("failure_reason"),
            }
            for cid, record in candidates_db.items()
        ]
    }


@app.get("/jobs/{job_id}/ranked-candidates", response_model=RankingResponse)
def rank_candidates_for_job(job_id: int, top_k: int = 5):
    """
    Rank analyzed candidates against a job description using
    semantic similarity search in Qdrant.
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = jobs_db[job_id]
    results = search_candidates(job["description"], top_k=top_k)

    ranked = [{"name": name, "score": score,"cv_text":cv_text} for name, score,cv_text in results]

    return {"job_id": job_id, "ranked_candidates": ranked}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Ask why a specific candidate is a good fit for a given job."""
    answer = explain_ranking(request.candidate_name, request.job_description)
    return {"answer": answer}