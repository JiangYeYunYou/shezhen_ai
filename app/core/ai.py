from pathlib import Path
from openai import AsyncOpenAI
from typing import AsyncGenerator

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

PROMPT_DIR = Path("prompts")


def load_system_prompt(prompt_file: str) -> str:
    prompt_path = PROMPT_DIR / prompt_file
    if not prompt_path.exists():
        logger.warning(f"System prompt file not found: {prompt_path}")
        return "你是一个有帮助的AI助手。"
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
        )
        self.model = settings.AI_MODEL_NAME
        self._system_prompt_cache: dict[str, str] = {}
    
    def get_system_prompt(self, prompt_file: str) -> str:
        if prompt_file not in self._system_prompt_cache:
            self._system_prompt_cache[prompt_file] = load_system_prompt(prompt_file)
        return self._system_prompt_cache[prompt_file]
    
    async def chat_stream(
        self, 
        user_message: str, 
        system_prompt_file: str = "system_prompt_wenzhen.txt"
    ) -> AsyncGenerator[str, None]:
        system_prompt = self.get_system_prompt(system_prompt_file)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        logger.info(f"AI chat request - model: {self.model}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield content
                    
        except Exception as e:
            logger.error(f"AI chat error: {e}", exc_info=True)
            yield f"[错误] AI服务暂时不可用，请稍后重试。"


ai_service = AIService()
