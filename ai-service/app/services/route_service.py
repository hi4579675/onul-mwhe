from __future__ import annotations

from app.models.schemas import AmbienceTag, PlanItem, RouteGenerateRequest, RouteGenerateSuccessResponse
from app.services.retrieve_service import RetrieveService


class RouteService:
    def __init__(self) -> None:
        self.retrieve_service = RetrieveService()

    async def generate(self, body: RouteGenerateRequest, correlation_id: str) -> RouteGenerateSuccessResponse:
        # 1. 카카오 API에서 장소 후보들을 긁어옴 
        candidates = await self.retrieve_service.retrieve(body.region, body.timeslots)

        if not candidates: 
            return RouteGenerateSuccessResponse(
                plan=[],
                fallback_used=True, # 빈 응답 반환
                unknown_count=0,
                correlation_id=correlation_id,
            )
        # 2. 리스트의 첫 번째 장소만 딱 골라서 하나 만듬
        first = candidates[0]
        plan = [
            PlanItem(
                place_id=first.place_id,
                slot=first.slot,
                order=1,
                reason=f"{body.region}에서 검색된 후보 기반 추천입니다.",
                confidence=0.65,
                ambience_tag=AmbienceTag.unknown,
            )
        ]
        return RouteGenerateSuccessResponse(
            plan=plan,
            fallback_used=False,
            unknown_count=1,
            correlation_id=correlation_id,
        )