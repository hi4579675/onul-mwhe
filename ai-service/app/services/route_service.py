from __future__ import annotations

from app.models.schemas import AmbienceTag, PlanItem, RouteGenerateRequest, RouteGenerateSuccessResponse
from app.services.feasibility_service import FeasibilityService
from app.services.retrieve_service import RetrieveService


class RouteService:
    def __init__(self) -> None:
        self.retrieve_service = RetrieveService()
        self.feasibility_service = FeasibilityService()

    async def generate(self, body: RouteGenerateRequest, correlation_id: str) -> RouteGenerateSuccessResponse:
        # 1. 카카오 API에서 장소 후보들을 긁어옴 
        candidates = await self.retrieve_service.retrieve(body.region, body.timeslots)
         # 2. 실현 가능성 필터 적용
        feasible = self.feasibility_service.apply(candidates, body.timeslots)

        # 3. 실현 가능성 필터 결과가 없으면 빈 응답 반환
        if not feasible:
            return RouteGenerateSuccessResponse(
                plan=[],
                fallback_used=True,
                unknown_count=0,
                correlation_id=correlation_id,
            )
            
        # 4.  MVP 임시 로직: 첫 후보 1개 선택
        first = feasible[0]
        plan = [
            PlanItem(
                place_id=first.place_id,
                slot=first.slot,
                order=1,
                reason=f"{body.region}에서 실현 가능한 후보 기반 추천입니다.",
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