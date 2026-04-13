import json
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Diagnosis(Base):
    __tablename__ = "diagnosis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    tongue_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    syndromes: Mapped[str] = mapped_column(Text, nullable=False)
    constitution: Mapped[str] = mapped_column(Text, nullable=False)
    health_score: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    advice: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tongue_surface_image: Mapped[bytes] = mapped_column(LONGBLOB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("ix_diagnosis_user_id", "user_id"),
        Index("ix_diagnosis_created_at", "created_at"),
    )
    
    @property
    def tongue_analysis_dict(self) -> dict:
        try:
            return json.loads(self.tongue_analysis) if self.tongue_analysis else {}
        except json.JSONDecodeError:
            return {}
    
    @tongue_analysis_dict.setter
    def tongue_analysis_dict(self, value: dict):
        self.tongue_analysis = json.dumps(value, ensure_ascii=False)
    
    @property
    def syndromes_list(self) -> list[str]:
        try:
            return json.loads(self.syndromes) if self.syndromes else []
        except json.JSONDecodeError:
            return []
    
    @syndromes_list.setter
    def syndromes_list(self, value: list[str]):
        self.syndromes = json.dumps(value, ensure_ascii=False)
    
    @property
    def constitution_dict(self) -> dict:
        try:
            return json.loads(self.constitution) if self.constitution else {}
        except json.JSONDecodeError:
            return {}
    
    @constitution_dict.setter
    def constitution_dict(self, value: dict):
        self.constitution = json.dumps(value, ensure_ascii=False)
    
    @property
    def health_score_dict(self) -> dict:
        try:
            return json.loads(self.health_score) if self.health_score else {}
        except json.JSONDecodeError:
            return {}
    
    @health_score_dict.setter
    def health_score_dict(self, value: dict):
        self.health_score = json.dumps(value, ensure_ascii=False)
