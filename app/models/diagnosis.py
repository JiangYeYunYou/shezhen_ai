import json
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Diagnosis(Base):
    __tablename__ = "diagnosis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    signs: Mapped[str] = mapped_column(Text, nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    advice: Mapped[str] = mapped_column(String(2000), nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("ix_diagnosis_user_id", "user_id"),
        Index("ix_diagnosis_created_at", "created_at"),
    )
    
    @property
    def signs_list(self) -> list[str]:
        try:
            return json.loads(self.signs) if self.signs else []
        except json.JSONDecodeError:
            return []
    
    @signs_list.setter
    def signs_list(self, value: list[str]):
        self.signs = json.dumps(value, ensure_ascii=False)
    
    @property
    def symptoms_list(self) -> list[str]:
        try:
            return json.loads(self.symptoms) if self.symptoms else []
        except json.JSONDecodeError:
            return []
    
    @symptoms_list.setter
    def symptoms_list(self, value: list[str]):
        self.symptoms = json.dumps(value, ensure_ascii=False)
    
    @property
    def advice_list(self) -> list[str]:
        try:
            return json.loads(self.advice) if self.advice else []
        except json.JSONDecodeError:
            return []
    
    @advice_list.setter
    def advice_list(self, value: list[str]):
        self.advice = json.dumps(value, ensure_ascii=False)
