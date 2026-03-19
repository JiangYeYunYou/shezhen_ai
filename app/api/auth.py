from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import generate_salt, hash_password, verify_password
from app.core.jwt import create_access_token
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenData, UserInfo
from app.schemas.response import ApiResponse, success_response, error_response

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse[UserInfo], summary="用户注册")
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == request.username))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return error_response(message="用户名已存在", code=400)
    
    salt = generate_salt()
    hashed_password = hash_password(request.password, salt)
    
    new_user = User(
        username=request.username,
        password=hashed_password,
        salt=salt
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return success_response(
        data=UserInfo(id=new_user.id, username=new_user.username),
        message="注册成功"
    )


@router.post("/login", response_model=ApiResponse[TokenData], summary="用户登录")
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()
    
    if not user:
        return error_response(message="用户名或密码错误", code=401)
    
    if not verify_password(request.password, user.salt, user.password):
        return error_response(message="用户名或密码错误", code=401)
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    
    return success_response(
        data=TokenData(access_token=access_token, token_type="bearer"),
        message="登录成功"
    )
