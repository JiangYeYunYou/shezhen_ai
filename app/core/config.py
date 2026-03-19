from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    APP_NAME: str = "Shezhen AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "Shezhenapp&root163"
    MYSQL_DATABASE: str = "shezhen_ai"
    
    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+aiomysql://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    AI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "deepseek-v3.2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
