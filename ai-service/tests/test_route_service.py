from __future__ import annotations

import asyncio

from app.models.schemas import Ambience, RouteGenerateRequest, TimeSlot
from app.services.feasibility_service import FeasibleCandidate
from app.services.route_service import RouteService
from app.services.score_service import ScoredCandidate


def _req(timeslots: list[TimeSlot]) -> RouteGenerateRequest:
    return RouteGenerateRequest(
        region="성수",
        timeslots=timeslots,
        preferred_ambience=[Ambience.cozy],
        food_type=[],
        budget_level="normal",
    )


def _fc(place_id: str, slot: TimeSlot) -> FeasibleCandidate:
    return FeasibleCandidate(
        place_id=place_id,
        name=place_id,
        slot=slot,
        lat=37.5,
        lng=127.0,
        travel_minutes=10,
        stay_minutes=60,
        penalty_score=0.0,
        open_at=True,
        category_name="카페",
        keywords=["cozy"],
    )


def _sc(place_id: str, slot: TimeSlot, score: float) -> ScoredCandidate:
    return ScoredCandidate(
        candidate=_fc(place_id, slot),
        final_score=score,
        confidence=0.8,
        ambience_tag="cozy",  # 실제 코드에서는 AmbienceTag.cozy 사용
    )


def test_route_service_keeps_requested_slot_order():
    service = RouteService()

    class StubRetrieve:
        async def retrieve(self, region, slots):
            return ["dummy"]

    class StubFeasibility:
        def apply(self, candidates, requested_slots):
            return [_fc("kakao_any", requested_slots[0])]

    class StubScore:
        def score(self, feasible, preferred):
            # 점수는 lunch가 가장 높지만, 최종 선택 순서는 요청 순서를 따라야 함
            return [
                _sc("kakao_lunch", TimeSlot.lunch, 0.95),
                _sc("kakao_dinner", TimeSlot.dinner, 0.70),
                _sc("kakao_cafe", TimeSlot.cafe, 0.60),
            ]

    service.retrieve_service = StubRetrieve()
    service.feasibility_service = StubFeasibility()
    service.score_service = StubScore()

    body = _req([TimeSlot.dinner, TimeSlot.cafe, TimeSlot.lunch])
    result = asyncio.run(service.generate(body, "cid-1"))

    assert [p.slot for p in result.plan] == [TimeSlot.dinner, TimeSlot.cafe, TimeSlot.lunch]


def test_route_service_prevents_duplicate_place_id():
    service = RouteService()

    class StubRetrieve:
        async def retrieve(self, region, slots):
            return ["dummy"]

    class StubFeasibility:
        def apply(self, candidates, requested_slots):
            return [_fc("kakao_any", requested_slots[0])]

    class StubScore:
        def score(self, feasible, preferred):
            return [
                _sc("kakao_dup", TimeSlot.lunch, 0.90),   # lunch 선택
                _sc("kakao_dup", TimeSlot.cafe, 0.89),    # cafe에서는 중복이라 스킵
                _sc("kakao_cafe2", TimeSlot.cafe, 0.50),  # 대체 후보 선택
                _sc("kakao_dinner", TimeSlot.dinner, 0.60),
            ]

    service.retrieve_service = StubRetrieve()
    service.feasibility_service = StubFeasibility()
    service.score_service = StubScore()

    body = _req([TimeSlot.lunch, TimeSlot.cafe, TimeSlot.dinner])
    result = asyncio.run(service.generate(body, "cid-2"))

    place_ids = [p.place_id for p in result.plan]
    assert len(place_ids) == len(set(place_ids))
    assert [p.slot for p in result.plan] == [TimeSlot.lunch, TimeSlot.cafe, TimeSlot.dinner]