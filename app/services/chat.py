from typing import AsyncGenerator
from app.core.ai import ai_service


class ChatService:
    def __init__(self):
        self.ai_service = ai_service
    
    async def wenzhen_chat(self, message: str) -> AsyncGenerator[str, None]:
        async for chunk in self.ai_service.chat_stream(
            user_message=message,
            system_prompt_file="system_prompt_wenzhen.txt"
        ):
            yield chunk


chat_service = ChatService()
