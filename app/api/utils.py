from datetime import date
from fastapi import APIRouter, Query

from app.schemas.lunar import LunarCalendarResponse
from app.schemas.response import ApiResponse, success_response, error_response
from app.schemas.tcm_tip import TCMTipItem
from app.services.lunar import lunar_service
from app.services.tcm_tip import get_random_tips
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


@router.get(
    "/tcm-tips",
    response_model=ApiResponse[list[TCMTipItem]],
    summary="获取随机中医小常识",
    description="从中医常识库中随机抽取 3 条小常识，每次请求返回结果不同。",
)
async def get_tcm_tips():
    """随机获取 3 条中医小常识。"""
    try:
        tips = get_random_tips(count=3)
        return success_response(data=tips, message="success")
    except FileNotFoundError:
        logger.error("中医常识数据文件不存在")
        return error_response(message="中医常识数据暂不可用，请稍后再试", code=500)
    except ValueError as e:
        logger.warning(f"中医常识数据不足：{e}")
        return error_response(message=str(e), code=500)
    except Exception as e:
        logger.error(f"获取中医小常识异常：{e}", exc_info=True)
        return error_response(message="获取中医小常识失败，请稍后再试", code=500)
