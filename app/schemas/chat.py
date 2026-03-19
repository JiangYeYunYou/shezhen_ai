from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("消息不能为空")
        if len(v) > 2000:
            raise ValueError("消息长度不能超过2000个字符")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "message": "最近总是感觉疲劳，睡眠也不好",
                "conversation_history": []
            }
        }
