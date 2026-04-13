import base64
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis import DiagnosisRepository
from app.models.diagnosis import Diagnosis
from app.core.vision import vision_service
from app.core.image_processor import process_tongue_image
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
        
        tongue_analysis = result.get("舌象分析", {})
        if tongue_analysis.get("舌色", {}).get("特征") == "未识别":
            raise ValueError(result.get("调理建议", "请上传清晰的舌头照片进行诊断。"))
        
        tongue_surface_image = None
        try:
            tongue_surface_bytes = base64.b64decode(tongue_surface_base64)
            tongue_surface_image = process_tongue_image(tongue_surface_bytes)
            logger.info(f"Tongue surface image processed: {len(tongue_surface_image)} bytes")
        except Exception as e:
            logger.error(f"Failed to process tongue surface image: {e}", exc_info=True)
        
        diagnosis = await self.repository.create(
            user_id=user_id,
            tongue_analysis=result.get("舌象分析", {}),
            syndromes=result.get("可能有以下的证型", []),
            constitution=result.get("体质分析", {}),
            health_score=result.get("健康评分", {}),
            advice=result.get("调理建议", ""),
            tongue_surface_image=tongue_surface_image
        )
        
        logger.info(f"Diagnosis created for user {user_id}, total score: {diagnosis.health_score_dict.get('总分', 0)}")
        
        return diagnosis
    
    async def get_user_diagnoses(self, user_id: int, limit: int = 10) -> list[Diagnosis]:
        return await self.repository.find_by_user_id(user_id, limit)
    
    async def get_diagnosis_by_id(self, diagnosis_id: int) -> Diagnosis | None:
        return await self.repository.find_by_id(diagnosis_id)
