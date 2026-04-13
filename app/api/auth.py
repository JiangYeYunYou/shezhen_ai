from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.user import UserService
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenData, UserInfo
from app.schemas.response import ApiResponse, success_response, error_response
from app.dependencies import get_user_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse[UserInfo], summary="用户注册")
async def register(
    request: UserRegisterRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.register(request)
        return success_response(
            data=UserInfo(id=user.id, username=user.username),
            message="注册成功"
        )
    except ValueError as e:
        return error_response(message=str(e), code=400)


@router.post("/login", response_model=ApiResponse[TokenData], summary="用户登录")
async def login(
    request: UserLoginRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        user, access_token = await service.login(request.username, request.password)
        return success_response(
            data=TokenData(access_token=access_token, token_type="bearer"),
            message="登录成功"
        )
    except ValueError as e:
        return error_response(message=str(e), code=401)


@router.delete("/user/{user_id}", response_model=ApiResponse[None], summary="删除用户", 
               description="⚠️ **警告：此接口仅供后端管理使用，前端请勿调用！**")
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """
    ⚠️ 警告：此接口仅供后端管理使用，前端请勿调用！
    
    根据用户ID删除用户账号及其所有相关数据。
    此操作不可逆，请谨慎使用。
    """
    success = await service.delete_by_id(user_id)
    if success:
        return success_response(data=None, message="用户删除成功")
    else:
        return error_response(message="用户不存在", code=404)
