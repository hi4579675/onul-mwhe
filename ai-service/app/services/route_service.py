from __future__ import annotations

import logging

from app.models.schemas import AmbienceTag, PlanItem, RouteGenerateRequest,RouteGenerateSuccessResponse,TimeSlot 
from app.models.schemas import TimeSlot
from app.services.feasibility_service import FeasibilityService
from app.services.retrieve_service import RetrieveService
from app.services.score_service import ScoreService, ScoredCandidate

logger = logging.getLogger(__name__)

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

        # 실현 가능성 필터 결과가 없으면 빈 응답 반환
        if not feasible:
            return RouteGenerateSuccessResponse(
                plan=[],
                fallback_used=True,
                unknown_count=0,
                correlation_id=correlation_id,
            )
            
         # 3. 점수화
        scored = self.score_service.score(feasible, body.preferred_ambience)
        if not scored:
            return RouteGenerateSuccessResponse(
                plan=[],
                fallback_used=True,
                unknown_count=0,
                correlation_id=correlation_id,
            )
            
        # 4. 슬롯 기준 버킷 구성 + 슬롯 내부 점수 내림차순 정렬
        by_slot: dict[TimeSlot, list[ScoredCandidate]] = {}
        for item in scored:
            by_slot.setdefault(item.candidate.slot, []).append(item)
        for slot_items in by_slot.values():
            slot_items.sort(key=lambda x: x.final_score, reverse=True)

        # 5. 핵심 규칙:
        #    - 요청 body.timeslots 순서대로 1개씩 뽑기
        #    - place_id 중복 금지
        selected: list[PlanItem] = []
        used_place_ids: set[str] = set()
        dropped_slots: list[str] = []
        
        for slot in body.timeslots:
            slot_items = by_slot.get(slot, [])
            picked: ScoredCandidate | None = None
            for item in slot_items:
                if item.candidate.place_id in used_place_ids:
                    continue
                picked = item
                break

            if picked is None:
                # 슬롯 채우기 실패는 내부 로깅용으로 누적
                dropped_slots.append(slot.value)
                continue
            used_place_ids.add(picked.candidate.place_id)
            selected.append(
                PlanItem(
                    place_id=picked.candidate.place_id,
                    slot=picked.candidate.slot,
                    order=len(selected) + 1,
                    reason=(
                        f"{body.region} {picked.candidate.slot.value} 추천, "
                        f"이동 {picked.candidate.travel_minutes}분, "
                        f"체류 {picked.candidate.stay_minutes}분, "
                        f"feasibility 페널티 {picked.candidate.penalty_score:+.2f}"
                    ),
                    confidence=picked.confidence,
                    ambience_tag=picked.ambience_tag,
                )
            )        
        if dropped_slots:
            logger.info(
                "[%s] route.generate dropped_slots=%s requested=%s selected_count=%d",
                correlation_id,
                dropped_slots,
                [s.value for s in body.timeslots],
                len(selected),
            )
        if not selected:
            return RouteGenerateSuccessResponse(
                plan=[],
                fallback_used=True,
                unknown_count=0,
                correlation_id=correlation_id,
            )

        unknown_count = sum(1 for p in selected if p.ambience_tag == AmbienceTag.unknown)
        return RouteGenerateSuccessResponse(
            plan=selected,
            fallback_used=False,
            unknown_count=unknown_count,
            correlation_id=correlation_id,
        )