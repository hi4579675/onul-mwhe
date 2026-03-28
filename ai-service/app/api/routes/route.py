import logging
from uuid import UUID

from fastapi import APIRouter, Header

from app.models.schemas import (
    AmbienceTag,
    PlanItem,
    RouteGenerateRequest,
    RouteGenerateSuccessResponse,
    TimeSlot,
)
from app.services.route_service import RouteService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/route", tags=["route"])
route_service = RouteService()
 
# 응답은 반드시 RouteGenerateSuccessResponse 규격을 지켜야 함
@router.post("/generate", response_model=RouteGenerateSuccessResponse)
async def generate_route(
    body: RouteGenerateRequest, # 사용자가 보낸 데이터 (request body
    x_correlation_id: UUID = Header(..., alias="X-Correlation-ID"), # 헤더에서 추적 ID 꺼내기
) -> RouteGenerateSuccessResponse:
    correlation_id = str(x_correlation_id)
    
    try:
        response = await route_service.generate(body, correlation_id)
        
        logger.info(
            "[%s] route.generate success region=%s slots=%d fallback=%s",
            correlation_id,
            body.region,
            len(body.timeslots),
            response.fallback_used,
        )
        return response
    
    except Exception as e:
        logger.exception("[%s] route.generate failed: %s", correlation_id, e)
        return RouteGenerateSuccessResponse(
            plan=[],
            fallback_used=True,
            unknown_count=0,
            correlation_id=correlation_id,
        )
        
    
    