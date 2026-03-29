from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  # 1. 환경 설정 (Spring의 application.yml 설정과 비슷함)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    # 2. 앱 기본 정보
    APP_NAME: str = "onul-mwhe-ai-service"
    
   # Kakao API
    KAKAO_REST_API_KEY: str = Field(..., min_length=1)
    KAKAO_BASE_URL: str = "https://dapi.kakao.com"
    KAKAO_TIMEOUT_SECONDS: float = Field(default=3.0, gt=0)
    KAKAO_CONNECT_TIMEOUT_SECONDS: float = Field(default=1.5, gt=0)
    
    # Kakao retry policy
    KAKAO_RETRY_MAX_ATTEMPTS: int = Field(default=2, ge=1, le=5)
    KAKAO_RETRY_MIN_WAIT_SECONDS: float = Field(default=0.2, gt=0)
    KAKAO_RETRY_MAX_WAIT_SECONDS: float = Field(default=1.0, gt=0)
    
    # Kakao circuit breaker policy
    KAKAO_CB_FAIL_MAX: int = Field(default=5, ge=1)
    KAKAO_CB_RESET_TIMEOUT_SECONDS: int = Field(default=30, ge=1)
    
    # Claude
    ANTHROPIC_API_KEY: str = Field(default="")
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_TIMEOUT: float = 10.0
    
    # Business
    MAX_CANDIDATES_PER_CATEGORY: int = Field(default=10, ge=1, le=30)
    CONFIDENCE_THRESHOLD: float = 0.4
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    TTL_CANDIDATES: int = 3600
    
@lru_cache
def get_settings() -> Settings:
    return Settings()
