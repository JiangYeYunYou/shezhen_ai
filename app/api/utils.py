from datetime import date
from fastapi import APIRouter, Query

from app.schemas.lunar import LunarCalendarResponse
from app.schemas.response import ApiResponse, success_response
from app.services.lunar import lunar_service
from app.core.logging import get_logger

router = APIRouter(prefix="/utils", tags=["工具类"])
logger = get_logger(__name__)


@router.get("/lunar", response_model=ApiResponse[LunarCalendarResponse], summary="获取农历信息")
async def get_lunar_info(
    date_str: str = Query(None, description="日期，格式：YYYY-MM-DD，默认今天")
):
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return success_response(
                data=None,
                message="日期格式错误，请使用 YYYY-MM-DD 格式"
            )
    else:
        target_date = None
    
    result = lunar_service.get_lunar_info(target_date)
    
    return success_response(
        data=result,
        message="获取农历信息成功"
    )
