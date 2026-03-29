from __future__ import annotations

from app.models.schemas import AmbienceTag, PlanItem, RouteGenerateRequest, RouteGenerateSuccessResponse
from app.services.feasibility_service import FeasibilityService
from app.services.retrieve_service import RetrieveService
from app.services.score_service import ScoreService


class RouteService:
    def __init__(self) -> None:
        self.retrieve_service = RetrieveService()
        self.feasibility_service = FeasibilityService()
        self.score_service = ScoreService()

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
        scored = self.score_service.score(feasible, body.preferred_ambience)
        if not scored:
            return RouteGenerateSuccessResponse(
                plan=[],
                fallback_used=True,
                unknown_count=0,
                correlation_id=correlation_id,
            )
        selected: list[PlanItem] = []
        used_slots: set[str] = set()
        
        for item in sorted(scored, key=lambda x: x.final_score, reverse=True):
            slot_value = item.candidate.slot.value
            if slot_value in used_slots:
                continue
            used_slots.add(slot_value)
            selected.append(
                PlanItem(
                    place_id=item.candidate.place_id,
                    slot=item.candidate.slot,
                    order=len(selected) + 1,
                    reason=(
                        f"{body.region} {slot_value} 추천, "
                        f"이동 {item.candidate.travel_minutes}분, "
                        f"체류 {item.candidate.stay_minutes}분, "
                        f"feasibility 페널티 {item.candidate.penalty_score:+.2f}"
                    ),
                    confidence=item.confidence,
                    ambience_tag=item.ambience_tag,
                )
            )

            if len(selected) >= len(body.timeslots):
                    break
        if not selected:
          return RouteGenerateSuccessResponse(
              plan=[],
              fallback_used=True,
              unknown_count=0,
              correlation_id=correlation_id,
          )
        unknown_count = sum(1 for p in selected if p.ambience_tag.value == "unknown")
        return RouteGenerateSuccessResponse(
            plan=selected,
            fallback_used=False,
            unknown_count=unknown_count,
            correlation_id=correlation_id,
        )
       