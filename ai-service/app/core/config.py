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
    
    # 3. 카카오 API 설정
    KAKAO_REST_API_KEY: str = Field(..., min_length=1)
    KAKAO_BASE_URL: str = "https://dapi.kakao.com"
    KAKAO_TIMEOUT_SECONDS: float = Field(default=3.0, gt=0)
    MAX_CANDIDATES_PER_CATEGORY: int = Field(default=10, ge=1, le=30)
  
  # 4. Claude LLM (나중에 쓸 것들 미리 준비)
    ANTHROPIC_API_KEY: str = Field(default="")
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022" # 최신 모델명으로 업데이트
    LLM_TIMEOUT: float = 10.0

    # 5. 비즈니스 로직 설정 (Scoring)
    MAX_CANDIDATES_PER_CATEGORY: int = Field(default=15, ge=1, le=30)
    CONFIDENCE_THRESHOLD: float = 0.4

    # 6. Redis 및 캐시 설정
    REDIS_URL: str = "redis://localhost:6379"
    TTL_CANDIDATES: int = 3600 # 1시간

@lru_cache
def get_settings() -> Settings:
    return Settings()