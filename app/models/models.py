"""
SQLAlchemy models for the ATS / resume-job matching engine.

Domain model:
- Recruiter creates a Job (title, description, required skills, min years exp)
- Candidate uploads a Resume (raw file -> parsed text + extracted fields)
- Candidate applies to a Job -> creates an Application
- The Application stores a MatchScore: NOT a single opaque number, but a
  breakdown (skill_overlap, semantic_similarity, experience_match) so a
  recruiter can see WHY a candidate ranked where they did. This is the
  single biggest thing that separates this from a toy "GPT says 87%" project.

Note on String lengths: MySQL requires an explicit length on VARCHAR
columns (unlike Postgres). UUID primary/foreign keys are always 36
characters, so those use String(36). Free-text fields use a generous
String length or Text where content could be long.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, Integer, Text, JSON, Boolean
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

UUID_LEN = 36


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(UUID_LEN), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_recruiter = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="recruiter")
    resumes = relationship("Resume", back_populates="candidate")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(UUID_LEN), primary_key=True, default=gen_uuid)
    recruiter_id = Column(String(UUID_LEN), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    # Stored as a JSON list of lowercase skill strings, e.g. ["python", "sql", "react"]
    required_skills = Column(JSON, nullable=False, default=list)
    min_years_experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    recruiter = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(UUID_LEN), primary_key=True, default=gen_uuid)
    candidate_id = Column(String(UUID_LEN), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    # Extracted at parse time (see app/services/resume_parser.py)
    extracted_skills = Column(JSON, nullable=False, default=list)
    years_experience = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(UUID_LEN), primary_key=True, default=gen_uuid)
    job_id = Column(String(UUID_LEN), ForeignKey("jobs.id"), nullable=False, index=True)
    resume_id = Column(String(UUID_LEN), ForeignKey("resumes.id"), nullable=False)
    candidate_id = Column(String(UUID_LEN), ForeignKey("users.id"), nullable=False)

    # --- Explainable score breakdown, each in [0, 1] ---
    skill_overlap_score = Column(Float, nullable=False)
    semantic_similarity_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False, index=True)
    matched_skills = Column(JSON, nullable=False, default=list)
    missing_skills = Column(JSON, nullable=False, default=list)

    applied_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
