import random
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger
from app.schemas.tcm_tip import TCMTipItem

logger = get_logger(__name__)

# 数据文件路径（项目根目录下的 doc/changshi.txt）
_DATA_FILE = Path(__file__).resolve().parent.parent.parent / "doc" / "changshi.txt"
_COUNT = 3

# 模块级缓存：首次加载后驻留内存，后续请求零 I/O
_cached_tips: Optional[list[TCMTipItem]] = None


def _load_tips() -> list[TCMTipItem]:
    """从 changshi.txt 解析所有中医常识条目。

    文件格式：每行一条，标题与内容用中文冒号「：」分隔。
    空行自动跳过。
    """
    tips: list[TCMTipItem] = []
    with open(_DATA_FILE, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            # 用第一个「：」拆分（全角冒号）
            sep = "："
            idx = line.find(sep)
            if idx == -1:
                logger.warning(f"跳过无法解析的行（第 {line_no} 行）：{line}")
                continue
            title = line[:idx].strip()
            content = line[idx + len(sep):].strip()
            if not title or not content:
                logger.warning(f"跳过空标题/空内容（第 {line_no} 行）：{line}")
                continue
            tips.append(TCMTipItem(title=title, content=content))
    return tips


def get_random_tips(count: int = _COUNT) -> list[TCMTipItem]:
    """随机抽取指定数量的中医常识。

    Args:
        count: 需要抽取的数量，默认 3。

    Returns:
        随机抽取的中医常识列表。

    Raises:
        FileNotFoundError: 数据文件不存在。
        ValueError: 有效条目不足 count 条。
    """
    global _cached_tips

    # 首次调用时加载并缓存
    if _cached_tips is None:
        if not _DATA_FILE.exists():
            logger.error(f"数据文件不存在：{_DATA_FILE}")
            raise FileNotFoundError(f"数据文件不存在：{_DATA_FILE}")
        _cached_tips = _load_tips()
        logger.info(f"已加载 {_cached_tips.__len__()} 条中医常识")

    if len(_cached_tips) < count:
        raise ValueError(
            f"有效常识条目不足，当前仅有 {len(_cached_tips)} 条，"
            f"无法抽取 {count} 条"
        )

    return random.sample(_cached_tips, count)
