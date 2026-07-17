from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Application, Job, Resume, User
from app.models.schemas import ApplicationOut, ApplyRequest
from app.services.matching_service import score_application

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut)
def apply_to_job(payload: ApplyRequest, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    job = db.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.get(Resume, payload.resume_id)
    if not resume or resume.candidate_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    existing = db.execute(
        select(Application).where(
            Application.job_id == job.id, Application.resume_id == resume.id
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied with this resume")

    # This is where the explainable scoring from matching_service.py runs.
    result = score_application(
        job_description=job.description,
        required_skills=job.required_skills,
        min_years_required=job.min_years_experience,
        resume_text=resume.raw_text,
        candidate_skills=resume.extracted_skills,
        candidate_years=resume.years_experience,
    )

    application = Application(
        job_id=job.id,
        resume_id=resume.id,
        candidate_id=current_user.id,
        skill_overlap_score=result["skill_overlap_score"],
        semantic_similarity_score=result["semantic_similarity_score"],
        experience_score=result["experience_score"],
        final_score=result["final_score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/job/{job_id}/ranked", response_model=list[ApplicationOut])
def ranked_candidates(job_id: str, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """
    The recruiter dashboard endpoint: every applicant for this job,
    sorted by final_score descending, WITH the full explainable
    breakdown for each — not just a bare ranking.
    """
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your job posting")

    return db.execute(
        select(Application)
        .where(Application.job_id == job_id)
        .order_by(desc(Application.final_score))
    ).scalars().all()
