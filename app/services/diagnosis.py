from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis import DiagnosisRepository
from app.models.diagnosis import Diagnosis
from app.core.vision import vision_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class DiagnosisService:
    def __init__(self, session: AsyncSession):
        self.repository = DiagnosisRepository(session)
    
    async def diagnose(
        self, 
        user_id: int, 
        tongue_surface_base64: str, 
        tongue_bottom_base64: str = None
    ) -> Diagnosis:
        result = await vision_service.diagnose_tongue(
            tongue_surface_base64, 
            tongue_bottom_base64
        )
        
        if not result.get("is_tongue", False):
            raise ValueError(result.get("advice", "请上传清晰的舌头照片进行诊断。"))
        
        diagnosis = await self.repository.create(
            user_id=user_id,
            signs=result.get("signs", ""),
            symptoms=result.get("symptoms", ""),
            score=result.get("score", 0)
        )
        
        logger.info(f"Diagnosis created for user {user_id}, score: {diagnosis.score}")
        
        return diagnosis
    
    async def get_user_diagnoses(self, user_id: int, limit: int = 10) -> list[Diagnosis]:
        return await self.repository.find_by_user_id(user_id, limit)
    
    async def get_diagnosis_by_id(self, diagnosis_id: int) -> Diagnosis | None:
        return await self.repository.find_by_id(diagnosis_id)
