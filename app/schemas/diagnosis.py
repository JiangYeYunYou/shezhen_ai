from datetime import datetime
from pydantic import BaseModel, Field


class TongueFeature(BaseModel):
    特征: str
    描述: str
    主病: str = ""


class TongueCoatingFeature(BaseModel):
    特征: str
    描述: str
    主病: str = ""


class SublingualVein(BaseModel):
    特征: str
    描述: str
    主病: str = ""


class TongueAnalysis(BaseModel):
    舌色: TongueFeature
    舌形: TongueFeature
    苔色: TongueFeature
    苔质: list[TongueCoatingFeature]
    舌下络脉: SublingualVein


class HealthScoreItem(BaseModel):
    得分: int = Field(ge=0)


class HealthScoreDetail(BaseModel):
    舌色健康度: HealthScoreItem
    舌形健康度: HealthScoreItem
    苔色健康度: HealthScoreItem
    苔质健康度: HealthScoreItem
    舌下络脉健康度: HealthScoreItem
    综合体质评估: HealthScoreItem
    总分: int = Field(ge=0, le=100)
    健康等级: str
    标签: str


class ConstitutionAnalysis(BaseModel):
    主体质: str
    副体质: str
    总体特征: str
    发病倾向: str


class TongueDiagnosisResponse(BaseModel):
    舌象分析: TongueAnalysis
    健康评分: HealthScoreDetail
    可能有以下的证型: list[str]
    体质分析: ConstitutionAnalysis
    调理建议: str


class DiagnosisBase(BaseModel):
    tongue_analysis: str
    syndromes: str
    constitution: str
    health_score: str
    advice: str


class DiagnosisCreate(BaseModel):
    pass


class DiagnosisResponse(BaseModel):
    id: int
    user_id: int
    tongue_analysis: dict
    syndromes: list[str]
    constitution: dict
    health_score: dict
    advice: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DiagnosisListResponse(BaseModel):
    total: int
    items: list[DiagnosisResponse]
