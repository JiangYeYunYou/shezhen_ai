from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": None
            }
        }


def success_response(data: Optional[T] = None, message: str = "success") -> ApiResponse[T]:
    return ApiResponse(code=200, message=message, data=data)


def error_response(message: str, code: int = 400) -> ApiResponse:
    return ApiResponse(code=code, message=message, data=None)
