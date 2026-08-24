from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.models.comparison import Comparison
from app.services.auth_service import get_current_user
from app.schemas.comparison import ComparisonOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_submissions = db.query(Submission).filter(Submission.user_id == current_user.id).count()
    total_comparisons = db.query(Comparison).filter(Comparison.user_id == current_user.id).count()

    avg_similarity = (
        db.query(func.avg(Comparison.final_score))
        .filter(Comparison.user_id == current_user.id)
        .scalar()
    ) or 0.0

    high_risk_cases = (
        db.query(Comparison)
        .filter(Comparison.user_id == current_user.id, Comparison.risk_level.in_(["High", "Very High"]))
        .count()
    )

    recent = (
        db.query(Comparison)
        .filter(Comparison.user_id == current_user.id)
        .order_by(desc(Comparison.created_at))
        .limit(5)
        .all()
    )

    return {
        "total_submissions": total_submissions,
        "total_comparisons": total_comparisons,
        "average_similarity": round(float(avg_similarity), 2),
        "high_risk_cases": high_risk_cases,
        "recent_comparisons": [ComparisonOut.model_validate(c) for c in recent],
    }
