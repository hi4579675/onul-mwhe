from uuid import UUID

from fastapi import APIRouter, Header

from app.models.schemas import (
    AmbienceTag,
    PlanItem,
    RouteGenerateRequest,
    RouteGenerateSuccessResponse,
    TimeSlot,
)

router = APIRouter(prefix="/api/v1/route", tags=["route"])


@router.post("/generate", response_model=RouteGenerateSuccessResponse)
async def generate_route(
    body: RouteGenerateRequest,
    x_correlation_id: UUID = Header(..., alias="X-Correlation-ID"),
) -> RouteGenerateSuccessResponse:
    # TODO: 실제 Retrieve/Feasibility/Score/LLM 파이프라인 연결
    first_slot = body.timeslots[0] if body.timeslots else TimeSlot.lunch

    sample_plan = [
        PlanItem(
            place_id="kakao_12345",
            slot=first_slot,
            order=1,
            reason=f"{body.region}에서 취향 기반으로 우선 추천한 장소입니다.",
            confidence=0.72,
            ambience_tag=AmbienceTag.cozy,
        )
    ]

    return RouteGenerateSuccessResponse(
        plan=sample_plan,
        fallback_used=False,
        unknown_count=0,
        correlation_id=str(x_correlation_id),
    )