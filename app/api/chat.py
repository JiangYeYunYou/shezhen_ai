from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.ai import ai_service
from app.core.logging import get_logger
from app.schemas.chat import ChatRequest
from app.schemas.response import ApiResponse, success_response, error_response

router = APIRouter(prefix="/chat", tags=["问诊"])
logger = get_logger(__name__)


@router.post("/wenzhen", summary="中医问诊")
async def wenzhen_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Wenzhen chat request: {request.message[:50]}...")
    
    async def generate():
        try:
            async for chunk in ai_service.chat_stream(
                user_message=request.message,
                system_prompt_file="system_prompt_wenzhen.txt",
                conversation_history=request.conversation_history
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"[错误] {str(e)}"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
