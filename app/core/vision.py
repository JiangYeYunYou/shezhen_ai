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
    
    async def diagnose_tongue(self, tongue_surface_base64: str, tongue_bottom_base64: str) -> dict:
        # 清除缓存以使用最新的提示词
        if "system_prompt_shezhen_v2_txt" in self._system_prompt_cache:
            del self._system_prompt_cache["system_prompt_shezhen_v2_txt"]
        system_prompt = self.get_system_prompt("system_prompt_shezhen_v2_txt")
        
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
        
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{tongue_bottom_base64}"}
        })
        content.append({
            "type": "text",
            "text": "这是舌底照片。请综合舌面和舌底两张照片进行全面分析。"
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
            return self._get_error_response(f"诊断服务暂时不可用，请稍后重试。错误: {str(e)}")
    
    def _parse_response(self, content: str) -> dict:
        try:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                tongue_analysis = result.get("舌象分析", {})
                health_score = result.get("健康评分", {})
                syndromes = result.get("可能有以下的证型", [])
                constitution = result.get("体质分析", {})
                advice = result.get("调理建议", "")
                
                return {
                    "舌象分析": {
                        "舌色": tongue_analysis.get("舌色", {"特征": "未识别", "描述": "", "主病": ""}),
                        "舌形": tongue_analysis.get("舌形", {"特征": "未识别", "描述": "", "主病": ""}),
                        "苔色": tongue_analysis.get("苔色", {"特征": "未识别", "描述": "", "主病": ""}),
                        "苔质": tongue_analysis.get("苔质", []),
                        "舌下络脉": tongue_analysis.get("舌下络脉", {"特征": "未识别", "描述": "", "主病": ""})
                    },
                    "健康评分": {
                        "舌色健康度": health_score.get("舌色健康度", {"得分": 0}),
                        "舌形健康度": health_score.get("舌形健康度", {"得分": 0}),
                        "苔色健康度": health_score.get("苔色健康度", {"得分": 0}),
                        "苔质健康度": health_score.get("苔质健康度", {"得分": 0}),
                        "舌下络脉健康度": health_score.get("舌下络脉健康度", {"得分": 0}),
                        "综合体质评估": health_score.get("综合体质评估", {"得分": 0}),
                        "总分": health_score.get("总分", 0),
                        "健康等级": health_score.get("健康等级", "未识别"),
                        "标签": health_score.get("标签", "")
                    },
                    "可能有以下的证型": syndromes if isinstance(syndromes, list) else [syndromes] if syndromes else [],
                    "体质分析": {
                        "主体质": constitution.get("主体质", "未识别"),
                        "副体质": constitution.get("副体质", ""),
                        "总体特征": constitution.get("总体特征", ""),
                        "发病倾向": constitution.get("发病倾向", "")
                    },
                    "调理建议": advice if advice else ""
                }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
        
        return self._get_error_response("无法解析诊断结果，请重试。")
    
    def _get_error_response(self, message: str) -> dict:
        return {
            "舌象分析": {
                "舌色": {"特征": "未识别", "描述": "", "主病": ""},
                "舌形": {"特征": "未识别", "描述": "", "主病": ""},
                "苔色": {"特征": "未识别", "描述": "", "主病": ""},
                "苔质": [],
                "舌下络脉": {"特征": "未识别", "描述": "", "主病": ""}
            },
            "健康评分": {
                "舌色健康度": {"得分": 0},
                "舌形健康度": {"得分": 0},
                "苔色健康度": {"得分": 0},
                "苔质健康度": {"得分": 0},
                "舌下络脉健康度": {"得分": 0},
                "综合体质评估": {"得分": 0},
                "总分": 0,
                "健康等级": "未识别",
                "标签": ""
            },
            "可能有以下的证型": [],
            "体质分析": {
                "主体质": "未识别",
                "副体质": "",
                "总体特征": "",
                "发病倾向": ""
            },
            "调理建议": message
        }


vision_service = VisionService()
