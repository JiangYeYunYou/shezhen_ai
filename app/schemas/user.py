import re
from pydantic import BaseModel, field_validator


class UserRegisterRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v:
            raise ValueError("用户名不能为空")
        
        pattern = re.compile(r"^[\u4e00-\u9fa5a-zA-Z]+$")
        if not pattern.match(v):
            raise ValueError("用户名只能包含中文字符或英文字符")
        
        if len(v) < 2 or len(v) > 7:
            raise ValueError("用户名长度必须为2到7个字符")
        
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("密码不能为空")
        
        if len(v) < 8 or len(v) > 21:
            raise ValueError("密码长度必须为8到21个字符")
        
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "张三",
                "password": "password123"
            }
        }


class UserLoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v:
            raise ValueError("用户名不能为空")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("密码不能为空")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "张三",
                "password": "password123"
            }
        }


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserInfo(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "张三"
            }
        }
