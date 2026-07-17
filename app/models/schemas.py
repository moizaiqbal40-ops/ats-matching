from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    is_recruiter: bool = False


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_recruiter: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: list[str]
    min_years_experience: int = 0


class JobOut(BaseModel):
    id: str
    title: str
    description: str
    required_skills: list[str]
    min_years_experience: int
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: str
    filename: str
    extracted_skills: list[str]
    years_experience: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ApplicationOut(BaseModel):
    id: str
    job_id: str
    resume_id: str
    candidate_id: str
    skill_overlap_score: float
    semantic_similarity_score: float
    experience_score: float
    final_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    applied_at: datetime

    class Config:
        from_attributes = True


class ApplyRequest(BaseModel):
    job_id: str
    resume_id: str
