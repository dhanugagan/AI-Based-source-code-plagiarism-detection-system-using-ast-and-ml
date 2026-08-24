import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.comparison import Comparison
from app.models.submission import Submission
from app.models.report import Report
from app.services.auth_service import get_current_user
from app.services.file_service import read_source, FileValidationError
from app.services.comparison_service import compare_code, ComparisonError
from app.report.pdf_generator import generate_report_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/{comparison_id}/generate")
def generate_report(comparison_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
        code_a = read_source(sub_a.stored_path)
        code_b = read_source(sub_b.stored_path)
        result = compare_code(code_a, code_b, sub_a.language)
        explanation = result["explanation"]
    except (FileValidationError, ComparisonError):
        explanation = ["Detailed structural explanation unavailable."]

    scores = {
        "ast_similarity": comparison.ast_similarity,
        "token_similarity": comparison.token_similarity,
        "structural_similarity": comparison.structural_similarity,
        "ml_score": comparison.ml_score,
        "final_score": comparison.final_score,
        "risk_level": comparison.risk_level,
    }

    report_path = generate_report_pdf(
        comparison_id=comparison.id,
        user_name=current_user.name,
        file_a_name=sub_a.filename if sub_a else "unknown",
        file_b_name=sub_b.filename if sub_b else "unknown",
        scores=scores,
        explanation=explanation,
    )

    report = Report(comparison_id=comparison.id, report_path=report_path)
    db.add(report)
    db.commit()
    db.refresh(report)

    return {"report_id": report.id, "comparison_id": comparison.id}


@router.get("/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    comparison = db.query(Comparison).filter(Comparison.id == report.comparison_id).first()
    if not comparison or comparison.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this report.")

    if not os.path.exists(report.report_path):
        raise HTTPException(status_code=404, detail="Report file is missing on the server.")

    return FileResponse(report.report_path, media_type="application/pdf", filename=os.path.basename(report.report_path))


@router.delete("/{report_id}", status_code=204)
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    comparison = db.query(Comparison).filter(Comparison.id == report.comparison_id).first()
    if not comparison or comparison.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this report.")

    if os.path.exists(report.report_path):
        os.remove(report.report_path)

    db.delete(report)
    db.commit()
    return None
