from fastapi import APIRouter
router = APIRouter(tags=["health"])  

@router.get("/health") # HTTP GET /health 요청이 오면 실행 
def health() -> dict[str, str]: # 이 함수는 {글자: 글자} 형태의 사전을 반환
    return {"status": "ok"} 