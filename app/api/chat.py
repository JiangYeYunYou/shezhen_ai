from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.services.chat import chat_service
from app.core.logging import get_logger
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["问诊"])
logger = get_logger(__name__)


@router.post("/wenzhen", summary="中医问诊")
async def wenzhen_chat(request: ChatRequest):
    logger.info(f"Wenzhen chat request: {request.message[:50]}...")
    
    async def generate():
        try:
            async for chunk in chat_service.wenzhen_chat(
                message=request.message,
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
