from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Job, User
from app.models.schemas import JobCreate, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobOut)
def create_job(payload: JobCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    if not current_user.is_recruiter:
        raise HTTPException(status_code=403, detail="Only recruiters can post jobs")

    job = Job(
        recruiter_id=current_user.id,
        title=payload.title,
        description=payload.description,
        required_skills=[s.lower() for s in payload.required_skills],
        min_years_experience=payload.min_years_experience,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.execute(select(Job)).scalars().all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
