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
        result = await self.session.execute(
            select(Diagnosis)
            .where(Diagnosis.user_id == user_id)
            .order_by(Diagnosis.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(
        self,
        user_id: int,
        signs: str,
        symptoms: str,
        score: int
    ) -> Diagnosis:
        diagnosis = Diagnosis(
            user_id=user_id,
            signs=signs,
            symptoms=symptoms,
            score=score
        )
        self.session.add(diagnosis)
        await self.session.flush()
        await self.session.refresh(diagnosis)
        return diagnosis
