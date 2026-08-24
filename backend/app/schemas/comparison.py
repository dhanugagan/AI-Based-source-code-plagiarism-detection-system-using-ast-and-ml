from pydantic import BaseModel
from datetime import datetime


class CompareRequest(BaseModel):
    submission1_id: int
    submission2_id: int


class ComparisonOut(BaseModel):
    id: int
    submission1_id: int
    submission2_id: int
    ast_similarity: float
    token_similarity: float
    structural_similarity: float
    ml_score: float
    final_score: float
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class ComparisonDetail(ComparisonOut):
    code_a: str
    code_b: str
    features_a: dict
    features_b: dict
    explanation: list[str]
