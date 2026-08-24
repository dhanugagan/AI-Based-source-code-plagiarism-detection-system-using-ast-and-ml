"""
Batch Comparison / Assignment Mode

Lets a user (typically a teacher role in a real deployment; here any
authenticated user acting on their own submissions) select 3+ submissions
and automatically generate the full pairwise plagiarism matrix described in
the spec's "Assignment Mode" advanced feature:

          S1     S2     S3     S4
    S1    --     82%    21%    15%
    S2    82%    --     19%    13%
    S3    21%    19%    --     76%
    S4    15%    13%    76%    --

Each pair is scored using the same comparison_service pipeline as a single
analysis, and persisted as a normal Comparison row so it also shows up in
history/dashboard/admin views.
"""
from itertools import combinations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.models.comparison import Comparison
from app.schemas.batch import BatchCompareRequest, BatchCompareResult, PairwiseResult
from app.services.auth_service import get_current_user
from app.services.file_service import read_source, FileValidationError
from app.services.comparison_service import compare_code, ComparisonError

router = APIRouter(prefix="/api/comparisons", tags=["batch"])

MAX_BATCH_SUBMISSIONS = 25  # keep pairwise O(n^2) analysis tractable interactively


@router.post("/batch", response_model=BatchCompareResult)
def batch_compare(
    payload: BatchCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ids = list(dict.fromkeys(payload.submission_ids))  # dedupe, preserve order
    if len(ids) < 3:
        raise HTTPException(status_code=400, detail="Select at least 3 submissions for batch/assignment comparison.")
    if len(ids) > MAX_BATCH_SUBMISSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Batch comparison supports at most {MAX_BATCH_SUBMISSIONS} submissions at a time.",
        )

    submissions = (
        db.query(Submission)
        .filter(Submission.id.in_(ids), Submission.user_id == current_user.id)
        .all()
    )
    found_ids = {s.id for s in submissions}
    missing = [i for i in ids if i not in found_ids]
    if missing:
        raise HTTPException(status_code=404, detail=f"Submissions not found: {missing}")

    by_id = {s.id: s for s in submissions}
    ordered = [by_id[i] for i in ids]

    n = len(ordered)
    matrix = [[0.0] * n for _ in range(n)]
    risk_matrix = [["--"] * n for _ in range(n)]
    pairs: list[PairwiseResult] = []

    sources = {}
    for sub in ordered:
        try:
            sources[sub.id] = read_source(sub.stored_path)
        except FileValidationError as exc:
            raise HTTPException(status_code=400, detail=f"Could not read {sub.filename}: {exc}") from exc

    for i, j in combinations(range(n), 2):
        sub_a, sub_b = ordered[i], ordered[j]
        try:
            result = compare_code(sources[sub_a.id], sources[sub_b.id], sub_a.language)
        except ComparisonError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        matrix[i][j] = matrix[j][i] = result["final_score"]
        risk_matrix[i][j] = risk_matrix[j][i] = result["risk_level"]

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

        pairs.append(
            PairwiseResult(
                submission1_id=sub_a.id,
                submission2_id=sub_b.id,
                filename1=sub_a.filename,
                filename2=sub_b.filename,
                final_score=result["final_score"],
                risk_level=result["risk_level"],
            )
        )

    db.commit()

    high_risk_pairs = [p for p in pairs if p.risk_level in ("High", "Very High")]
    high_risk_pairs.sort(key=lambda p: p.final_score, reverse=True)

    return BatchCompareResult(
        submission_ids=[s.id for s in ordered],
        filenames=[s.filename for s in ordered],
        matrix=matrix,
        risk_matrix=risk_matrix,
        pairs=pairs,
        high_risk_pairs=high_risk_pairs,
    )
