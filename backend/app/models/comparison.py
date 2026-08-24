from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    submission1_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    submission2_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)

    ast_similarity = Column(Float, nullable=False)
    token_similarity = Column(Float, nullable=False)
    structural_similarity = Column(Float, nullable=False)
    ml_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
