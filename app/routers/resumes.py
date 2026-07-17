from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import MAX_UPLOAD_SIZE_MB
from app.models.models import Resume, User
from app.models.schemas import ResumeOut
from app.services.resume_parser import parse_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not (file.filename.lower().endswith(".pdf") or file.filename.lower().endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are accepted")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_UPLOAD_SIZE_MB}MB limit")

    try:
        parsed = parse_resume(file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    resume = Resume(
        candidate_id=current_user.id,
        filename=file.filename,
        raw_text=parsed["raw_text"],
        extracted_skills=parsed["skills"],
        years_experience=parsed["years_experience"],
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/mine", response_model=list[ResumeOut])
def my_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [r for r in current_user.resumes]
