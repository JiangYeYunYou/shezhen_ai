import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnosis import Diagnosis


class DiagnosisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, diagnosis_id: int) -> Diagnosis | None:
        result = await self.session.execute(
            select(Diagnosis).where(Diagnosis.id == diagnosis_id)
        )
        return result.scalar_one_or_none()
    
    async def find_by_user_id(self, user_id: int, limit: int = 10) -> list[Diagnosis]:
        query = (
            select(Diagnosis)
            .where(Diagnosis.user_id == user_id)
            .order_by(Diagnosis.created_at.desc())
        )
        if limit > 0:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(
        self,
        user_id: int,
        tongue_analysis: dict,
        syndromes: list[str],
        constitution: dict,
        health_score: dict,
        advice: str = "",
        tongue_surface_image: bytes = None
    ) -> Diagnosis:
        diagnosis = Diagnosis(
            user_id=user_id,
            tongue_analysis=json.dumps(tongue_analysis, ensure_ascii=False),
            syndromes=json.dumps(syndromes, ensure_ascii=False),
            constitution=json.dumps(constitution, ensure_ascii=False),
            health_score=json.dumps(health_score, ensure_ascii=False),
            advice=advice,
            tongue_surface_image=tongue_surface_image
        )
        self.session.add(diagnosis)
        await self.session.flush()
        await self.session.refresh(diagnosis)
        return diagnosis
