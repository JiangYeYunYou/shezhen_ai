from datetime import datetime
from pydantic import BaseModel, Field


class DiagnosisBase(BaseModel):
    signs: str
    symptoms: str
    score: int = Field(ge=0, le=100)


class DiagnosisCreate(BaseModel):
    pass


class DiagnosisResponse(DiagnosisBase):
    id: int
    user_id: int
    created_at: datetime
    advice: str = ""
    
    class Config:
        from_attributes = True


class DiagnosisListResponse(BaseModel):
    total: int
    items: list[DiagnosisResponse]


class TongueDiagnosisResponse(BaseModel):
    is_tongue: bool
    signs: str
    symptoms: str
    score: int = Field(ge=0, le=100)
    advice: str
