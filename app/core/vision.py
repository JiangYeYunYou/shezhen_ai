import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from pathlib import Path

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


class VisionService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_VISION_BASE_URL,
        )
        self.model = settings.AI_VISION_MODEL_NAME
        self._system_prompt_cache: dict[str, str] = {}
    
    def get_system_prompt(self, prompt_file: str) -> str:
        if prompt_file not in self._system_prompt_cache:
            self._system_prompt_cache[prompt_file] = load_system_prompt(prompt_file)
        return self._system_prompt_cache[prompt_file]
    
    async def diagnose_tongue(self, image_base64: str) -> dict:
        system_prompt = self.get_system_prompt("system_prompt_shezhen.txt")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    },
                    {
                        "type": "text",
                        "text": "请根据这张舌头照片进行诊断分析。"
                    }
                ]
            }
        ]
        
        logger.info(f"Vision diagnosis request - model: {self.model}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            
            content = response.choices[0].message.content
            logger.info(f"Vision response: {content[:200]}...")
            
            result = self._parse_response(content)
            return result
            
        except Exception as e:
            logger.error(f"Vision diagnosis error: {e}", exc_info=True)
            return {
                "is_tongue": False,
                "signs": "",
                "symptoms": "",
                "score": 0,
                "advice": f"诊断服务暂时不可用，请稍后重试。错误: {str(e)}"
            }
    
    def _parse_response(self, content: str) -> dict:
        try:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
        
        return {
            "is_tongue": False,
            "signs": "",
            "symptoms": "",
            "score": 0,
            "advice": "无法解析诊断结果，请重试。"
        }


vision_service = VisionService()
