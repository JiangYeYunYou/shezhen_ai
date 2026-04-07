import base64
import json
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse

from app.dependencies import get_current_user, get_diagnosis_service
from app.models.user import User
from app.services.diagnosis import DiagnosisService
from app.services.chat import chat_service
from app.schemas.diagnosis import DiagnosisResponse, DiagnosisListResponse, TongueDiagnosisResponse
from app.schemas.chat import ChatRequest
from app.schemas.response import ApiResponse, success_response, error_response
from app.core.logging import get_logger

router = APIRouter(prefix="/consultation", tags=["问诊舌诊"])
logger = get_logger(__name__)


@router.post("/wenzhen", summary="中医问诊")
async def wenzhen_chat(
    request: ChatRequest
):
    logger.info(f"Wenzhen chat request: {request.message[:50]}...")
    
    async def generate():
        try:
            async for chunk in chat_service.wenzhen_chat(message=request.message):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.post("/tongue", response_model=ApiResponse[TongueDiagnosisResponse], summary="舌诊分析")
async def diagnose_tongue(
    tongue_surface: UploadFile = File(..., description="舌面照片"),
    tongue_bottom: UploadFile = File(None, description="舌底照片（可选）"),
    current_user: User = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    
    if tongue_surface.content_type not in allowed_types:
        return error_response(message="舌面照片仅支持 JPG、PNG 格式", code=400)
    
    if tongue_bottom and tongue_bottom.content_type not in allowed_types:
        return error_response(message="舌底照片仅支持 JPG、PNG 格式", code=400)
    
    try:
        tongue_surface_data = await tongue_surface.read()
        tongue_surface_base64 = base64.b64encode(tongue_surface_data).decode("utf-8")
        
        tongue_bottom_base64 = None
        if tongue_bottom:
            tongue_bottom_data = await tongue_bottom.read()
            tongue_bottom_base64 = base64.b64encode(tongue_bottom_data).decode("utf-8")
        
        diagnosis = await service.diagnose(
            current_user.id, 
            tongue_surface_base64, 
            tongue_bottom_base64
        )
        
        return success_response(
            data=TongueDiagnosisResponse(
                is_tongue=True,
                signs=diagnosis.signs_list,
                symptoms=diagnosis.symptoms_list,
                score=diagnosis.score,
                advice=diagnosis.advice_list
            ),
            message="舌诊分析完成"
        )
    except ValueError as e:
        return success_response(
            data=TongueDiagnosisResponse(
                is_tongue=False,
                signs=[],
                symptoms=[],
                score=0,
                advice=[str(e)]
            ),
            message="舌诊分析完成"
        )
    except Exception as e:
        logger.error(f"Tongue diagnosis error: {e}", exc_info=True)
        return error_response(message="舌诊分析失败，请稍后重试", code=500)


@router.get("/history", response_model=ApiResponse[DiagnosisListResponse], summary="获取诊断历史")
async def get_diagnosis_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    diagnoses = await service.get_user_diagnoses(current_user.id, limit)
    
    items = [
        DiagnosisResponse(
            id=d.id,
            user_id=d.user_id,
            signs=d.signs_list,
            symptoms=d.symptoms_list,
            score=d.score,
            created_at=d.created_at,
            advice=d.advice_list
        )
        for d in diagnoses
    ]
    
    return success_response(
        data=DiagnosisListResponse(total=len(items), items=items),
        message="获取诊断历史成功"
    )


@router.get("/{diagnosis_id}", response_model=ApiResponse[DiagnosisResponse], summary="获取诊断详情")
async def get_diagnosis_detail(
    diagnosis_id: int,
    current_user: User = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    diagnosis = await service.get_diagnosis_by_id(diagnosis_id)
    
    if diagnosis is None:
        return error_response(message="诊断记录不存在", code=404)
    
    if diagnosis.user_id != current_user.id:
        return error_response(message="无权访问该诊断记录", code=403)
    
    return success_response(
        data=DiagnosisResponse(
            id=diagnosis.id,
            user_id=diagnosis.user_id,
            signs=diagnosis.signs_list,
            symptoms=diagnosis.symptoms_list,
            score=diagnosis.score,
            created_at=diagnosis.created_at,
            advice=diagnosis.advice_list
        ),
        message="获取诊断详情成功"
    )
