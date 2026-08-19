"""
crud.py
Database operations (Create/Read/Update/Delete) for candidates.
"""

from sqlalchemy.orm import Session

from models import Candidate, Skill,Job


def get_or_create_skill(db: Session, skill_name: str) -> Skill:
    """Return an existing Skill row by name, or create one if it doesn't exist."""
    skill = db.query(Skill).filter(Skill.name.ilike(skill_name)).first()
    if skill:
        return skill

    skill = Skill(name=skill_name)
    db.add(skill)
    db.flush()  # get the new skill.id without a full commit yet
    return skill


def create_candidate(db: Session, filename: str, cv_path: str) -> Candidate:
    """Create a new candidate record at upload time (before analysis)."""
    candidate = Candidate(name=None, cv_path=cv_path, status="uploaded")
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def save_extracted_info(db: Session, candidate: Candidate, cv_text: str, info: dict) -> Candidate:
    """Persist extracted candidate info (name, skills, experience, education) to the DB."""
    candidate.cv_text = cv_text
    candidate.name = info.get("name")
    candidate.experience_years = info.get("experience_years")
    candidate.education = info.get("education")
    candidate.status = "analyzed"

    skill_names = info.get("skills", []) or []
    candidate.skills = [get_or_create_skill(db, name) for name in skill_names]

    db.commit()
    db.refresh(candidate)
    return candidate


def mark_candidate_failed(db: Session, candidate: Candidate, reason: str) -> Candidate:
    """Mark a candidate as failed with a reason, and persist it."""
    candidate.status = "failed"
    candidate.failure_reason = reason
    db.commit()
    db.refresh(candidate)
    return candidate

def create_job(db: Session, description: str, profile: dict) -> Job:
    """Create a job record with its extracted structured profile."""
    job = Job(
        description=description,
        role=profile.get("role"),
        required_skills=",".join(profile.get("required_skills", []) or []),
        nice_to_have_skills=",".join(profile.get("nice_to_have_skills", []) or []),
        experience_required=profile.get("experience_required"),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def compute_skill_match(candidate_skills: list[str], required_skills: list[str]) -> dict:
    """Compare candidate skills against a job's required skills."""
    candidate_set = {s.strip().lower() for s in candidate_skills if s.strip()}
    required_set = {s.strip().lower() for s in required_skills if s.strip()}

    matching_lower = candidate_set & required_set
    missing_lower = required_set - candidate_set

    # Map back to original casing for display, using the required_skills list as source of truth
    original_required = {s.strip().lower(): s.strip() for s in required_skills if s.strip()}

    matching = [original_required[s] for s in matching_lower]
    missing = [original_required[s] for s in missing_lower]

    return {"matching_skills": matching, "missing_skills": missing}


def get_job(db: Session, job_id: int) -> Job | None:
    return db.query(Job).filter(Job.id == job_id).first()


def get_all_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()


def job_skills_as_list(job: Job) -> dict:
    """Convert a Job's comma-separated skill strings back into lists for API responses."""
    return {
        "required_skills": job.required_skills.split(",") if job.required_skills else [],
        "nice_to_have_skills": job.nice_to_have_skills.split(",") if job.nice_to_have_skills else [],
    }

def get_candidate(db: Session, candidate_id: int) -> Candidate | None:
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()


def get_all_candidates(db: Session) -> list[Candidate]:
    return db.query(Candidate).all()