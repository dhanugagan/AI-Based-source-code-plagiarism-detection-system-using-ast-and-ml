from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.models.comparison import Comparison
from app.schemas.comparison import CompareRequest, ComparisonOut, ComparisonDetail
from app.services.auth_service import get_current_user
from app.services.file_service import read_source, FileValidationError
from app.services.comparison_service import compare_code, ComparisonError

router = APIRouter(prefix="/api/comparisons", tags=["comparisons"])


def _get_owned_submission(db: Session, submission_id: int, user_id: int) -> Submission:
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.user_id == user_id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found.")
    return submission


@router.post("/analyze", response_model=ComparisonDetail, status_code=201)
def analyze(payload: CompareRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.submission1_id == payload.submission2_id:
        raise HTTPException(status_code=400, detail="Select two different submissions to compare.")

    sub_a = _get_owned_submission(db, payload.submission1_id, current_user.id)
    sub_b = _get_owned_submission(db, payload.submission2_id, current_user.id)

    try:
        code_a = read_source(sub_a.stored_path)
        code_b = read_source(sub_b.stored_path)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        result = compare_code(code_a, code_b, sub_a.language)
    except ComparisonError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    comparison = Comparison(
        user_id=current_user.id,
        submission1_id=sub_a.id,
        submission2_id=sub_b.id,
        ast_similarity=result["ast_similarity"],
        token_similarity=result["token_similarity"],
        structural_similarity=result["structural_similarity"],
        ml_score=result["ml_score"],
        final_score=result["final_score"],
        risk_level=result["risk_level"],
    )
    db.add(comparison)
    db.commit()
    db.refresh(comparison)

    return ComparisonDetail(
        id=comparison.id,
        submission1_id=comparison.submission1_id,
        submission2_id=comparison.submission2_id,
        ast_similarity=comparison.ast_similarity,
        token_similarity=comparison.token_similarity,
        structural_similarity=comparison.structural_similarity,
        ml_score=comparison.ml_score,
        final_score=comparison.final_score,
        risk_level=comparison.risk_level,
        created_at=comparison.created_at,
        code_a=code_a,
        code_b=code_b,
        features_a=result["features_a"],
        features_b=result["features_b"],
        explanation=result["explanation"],
    )


@router.get("", response_model=list[ComparisonOut])
def list_comparisons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Comparison)
        .filter(Comparison.user_id == current_user.id)
        .order_by(desc(Comparison.created_at))
        .all()
    )


@router.get("/{comparison_id}", response_model=ComparisonDetail)
def get_comparison(comparison_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comparison = (
        db.query(Comparison)
        .filter(Comparison.id == comparison_id, Comparison.user_id == current_user.id)
        .first()
    )
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found.")

    sub_a = db.query(Submission).filter(Submission.id == comparison.submission1_id).first()
    sub_b = db.query(Submission).filter(Submission.id == comparison.submission2_id).first()

    try:
        code_a = read_source(sub_a.stored_path) if sub_a else ""
        code_b = read_source(sub_b.stored_path) if sub_b else ""
    except FileValidationError:
        code_a, code_b = "", ""

    # Recompute lightweight explanation/features for display (not persisted
    # individually to keep the schema simple for this reference project).
    try:
        result = compare_code(code_a, code_b, sub_a.language if sub_a else "python")
        explanation = result["explanation"]
        features_a = result["features_a"]
        features_b = result["features_b"]
    except ComparisonError:
        explanation, features_a, features_b = [], {}, {}

    return ComparisonDetail(
        id=comparison.id,
        submission1_id=comparison.submission1_id,
        submission2_id=comparison.submission2_id,
        ast_similarity=comparison.ast_similarity,
        token_similarity=comparison.token_similarity,
        structural_similarity=comparison.structural_similarity,
        ml_score=comparison.ml_score,
        final_score=comparison.final_score,
        risk_level=comparison.risk_level,
        created_at=comparison.created_at,
        code_a=code_a,
        code_b=code_b,
        features_a=features_a,
        features_b=features_b,
        explanation=explanation,
    )
