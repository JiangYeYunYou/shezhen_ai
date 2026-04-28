from pydantic import BaseModel


class TCMTipItem(BaseModel):
    """单条中医常识"""
    title: str
    content: str

    class Config:
        json_schema_extra = {
            "examples": [
                {"title": "阴阳学说", "content": "万物分阴阳，健康是阴阳动态平衡，疾病是阴阳失调。"}
            ]
        }
