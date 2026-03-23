import json
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
    
    async def diagnose_tongue(self, tongue_surface_base64: str, tongue_bottom_base64: str = None) -> dict:
        system_prompt = self.get_system_prompt("system_prompt_shezhen.txt")
        
        content = [
            {
                "type": "text",
                "text": "请根据以下舌头照片进行诊断分析。"
            }
        ]
        
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{tongue_surface_base64}"}
        })
        content.append({
            "type": "text",
            "text": "这是舌面照片。"
        })
        
        if tongue_bottom_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{tongue_bottom_base64}"}
            })
            content.append({
                "type": "text",
                "text": "这是舌底照片。请综合舌面和舌底两张照片进行诊断分析。"
            })
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
        
        logger.info(f"Vision diagnosis request - model: {self.model}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            
            result_content = response.choices[0].message.content
            logger.info(f"Vision response: {result_content[:200]}...")
            
            result = self._parse_response(result_content)
            return result
            
        except Exception as e:
            logger.error(f"Vision diagnosis error: {e}", exc_info=True)
            return {
                "is_tongue": False,
                "signs": [],
                "symptoms": [],
                "score": 0,
                "advice": [f"诊断服务暂时不可用，请稍后重试。错误: {str(e)}"]
            }
    
    def _parse_response(self, content: str) -> dict:
        try:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                result["signs"] = self._ensure_list(result.get("signs", []))
                result["symptoms"] = self._ensure_list(result.get("symptoms", []))
                result["advice"] = self._ensure_list(result.get("advice", []))
                
                return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
        
        return {
            "is_tongue": False,
            "signs": [],
            "symptoms": [],
            "score": 0,
            "advice": ["无法解析诊断结果，请重试。"]
        }
    
    def _ensure_list(self, value) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value] if value else []
        return []


vision_service = VisionService()
