from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.models.comparison import Comparison
from app.schemas.auth import UserOut
from app.schemas.comparison import ComparisonOut
from app.schemas.submission import SubmissionOut
from app.services.auth_service import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/submissions", response_model=list[SubmissionOut])
def list_all_submissions(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Submission).order_by(desc(Submission.uploaded_at)).all()


@router.get("/comparisons", response_model=list[ComparisonOut])
def list_all_comparisons(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Comparison).order_by(desc(Comparison.created_at)).all()


@router.get("/comparisons/high-risk", response_model=list[ComparisonOut])
def high_risk_comparisons(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return (
        db.query(Comparison)
        .filter(Comparison.risk_level.in_(["High", "Very High"]))
        .order_by(desc(Comparison.created_at))
        .all()
    )


@router.get("/statistics")
def system_statistics(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    total_users = db.query(User).count()
    total_submissions = db.query(Submission).count()
    total_comparisons = db.query(Comparison).count()
    avg_similarity = db.query(func.avg(Comparison.final_score)).scalar() or 0.0
    high_risk = db.query(Comparison).filter(Comparison.risk_level.in_(["High", "Very High"])).count()

    return {
        "total_users": total_users,
        "total_submissions": total_submissions,
        "total_comparisons": total_comparisons,
        "average_similarity": round(float(avg_similarity), 2),
        "high_risk_cases": high_risk,
    }


@router.delete("/submissions/{submission_id}", status_code=204)
def admin_delete_submission(submission_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    import os

    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if os.path.exists(submission.stored_path):
        os.remove(submission.stored_path)
    db.delete(submission)
    db.commit()
    return None
