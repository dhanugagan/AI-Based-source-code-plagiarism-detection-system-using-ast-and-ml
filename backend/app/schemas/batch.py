from pydantic import BaseModel
from typing import List


class BatchCompareRequest(BaseModel):
    submission_ids: List[int]


class PairwiseResult(BaseModel):
    submission1_id: int
    submission2_id: int
    filename1: str
    filename2: str
    final_score: float
    risk_level: str


class BatchCompareResult(BaseModel):
    submission_ids: List[int]
    filenames: List[str]
    matrix: List[List[float]]  # final_score matrix, symmetric, diagonal = 0
    risk_matrix: List[List[str]]
    pairs: List[PairwiseResult]
    high_risk_pairs: List[PairwiseResult]
