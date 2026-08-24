from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.schemas.submission import SubmissionOut
from app.services.auth_service import get_current_user
from app.services.file_service import save_upload, read_source, FileValidationError
import os

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post("/upload", response_model=SubmissionOut, status_code=201)
async def upload_submission(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        saved = await save_upload(file, current_user.id)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    submission = Submission(
        user_id=current_user.id,
        filename=saved["filename"],
        stored_path=saved["stored_path"],
        language=saved["language"],
        file_size=saved["file_size"],
        code_hash=saved["code_hash"],
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("", response_model=list[SubmissionOut])
def list_submissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(desc(Submission.uploaded_at))
        .all()
    )


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.user_id == current_user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission


@router.get("/{submission_id}/source")
def get_submission_source(submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Read-only source preview, used by the Compare page's editor panes."""
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.user_id == current_user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    try:
        source = read_source(submission.stored_path)
    except FileValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"id": submission.id, "filename": submission.filename, "language": submission.language, "source": source}


@router.delete("/{submission_id}", status_code=204)
def delete_submission(submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.user_id == current_user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if os.path.exists(submission.stored_path):
        os.remove(submission.stored_path)

    db.delete(submission)
    db.commit()
    return None
