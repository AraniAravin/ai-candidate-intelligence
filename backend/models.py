"""
models.py
SQLAlchemy ORM models: Candidates, Jobs, Skills, Applications, Match Results.
"""

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

# Many-to-many join table: candidates <-> skills
candidate_skills = Table(
    "candidate_skills",
    Base.metadata,
    Column("candidate_id", Integer, ForeignKey("candidates.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    candidates = relationship("Candidate", secondary=candidate_skills, back_populates="skills")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    cv_path = Column(String, nullable=False)
    cv_text = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    education = Column(String, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, processing, analyzed, failed
    failure_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    skills = relationship("Skill", secondary=candidate_skills, back_populates="candidates")
    applications = relationship("Application", back_populates="candidate")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    role = Column(String, nullable=True)
    required_skills = Column(Text, nullable=True)      # stored as comma-separated for now
    nice_to_have_skills = Column(Text, nullable=True)  # stored as comma-separated for now
    experience_required = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship("Application", back_populates="job")


class Application(Base):
    """Links a candidate to a job — 'this candidate is being considered for this job'."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    match_result = relationship("MatchResult", back_populates="application", uselist=False)


class MatchResult(Base):
    """Computed match outcome for a specific candidate-job application."""
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, unique=True)
    semantic_score = Column(Float, nullable=True)
    matching_skills = Column(Text, nullable=True)  # comma-separated for now
    missing_skills = Column(Text, nullable=True)   # comma-separated for now
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="match_result")