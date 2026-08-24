from pydantic import BaseModel
from datetime import datetime


class SubmissionOut(BaseModel):
    id: int
    filename: str
    language: str
    file_size: int
    code_hash: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
