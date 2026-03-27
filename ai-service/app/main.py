from fastapi import FastAPI
from app.api.routes.health import router as health_router # 건강검진 주방 가져오기
from app.api.routes.route import router as route_router # 동선 생성 주방 가져오기

# 전체 서비스(FastAPI) 인스턴스 생성
app = FastAPI(
    title="onul-mwhe ai-service", # 앱 이름
    version="0.1.0", # 버전
)

app.include_router(health_router)
app.include_router(route_router)