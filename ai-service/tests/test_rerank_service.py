from __future__ import annotations

import asyncio

from app.models.schemas import Ambience, AmbienceTag, TimeSlot
from app.services.feasibility_service import FeasibleCandidate
from app.services.rerank_service import RerankService
from app.services.score_service import ScoredCandidate


def _sc(place_id: str, score: float) -> ScoredCandidate:
    return ScoredCandidate(
        candidate=FeasibleCandidate(
            place_id=place_id,
            name=place_id,
            slot=TimeSlot.cafe,
            lat=37.5,
            lng=127.0,
            travel_minutes=10,
            stay_minutes=60,
            penalty_score=0.0,
            open_at=True,
            category_name="카페",
            keywords=["cozy"],
        ),
        final_score=score,
        confidence=0.8,
        ambience_tag=AmbienceTag.cozy,
    )


def test_rerank_allowlist_filters_non_candidate_place_id(monkeypatch):
    service = RerankService(model="test-model", timeout_seconds=1.0)
    candidates = [_sc("kakao_1", 0.9), _sc("kakao_2", 0.8)]
    allowlist = {"kakao_1", "kakao_2"}

    async def fake_llm(*args, **kwargs):
        return [
            {"place_id": "kakao_999", "reason": "환각 id"},  # allowlist 밖
            {"place_id": "kakao_2", "reason": "정상"},
            {"place_id": "kakao_1", "reason": "정상"},
        ]

    monkeypatch.setattr(service, "_call_llm_mvp", fake_llm)

    reranked, reason_map = asyncio.run(
        service.rerank_slot_candidates(
            slot=TimeSlot.cafe,
            candidates=candidates,
            region="성수",
            preferred_ambience=[Ambience.cozy],
            allowlist=allowlist,
        )
    )

    assert [x.candidate.place_id for x in reranked] == ["kakao_2", "kakao_1"]
    assert "kakao_999" not in reason_map


def test_rerank_timeout_falls_back_to_original_order(monkeypatch):
    service = RerankService(model="test-model", timeout_seconds=0.01)
    candidates = [_sc("kakao_1", 0.9), _sc("kakao_2", 0.8)]

    async def slow_llm(*args, **kwargs):
        await asyncio.sleep(0.05)
        return [{"place_id": "kakao_2", "reason": "늦게 도착"}]

    monkeypatch.setattr(service, "_call_llm_mvp", slow_llm)

    reranked, reason_map = asyncio.run(
        service.rerank_slot_candidates(
            slot=TimeSlot.cafe,
            candidates=candidates,
            region="성수",
            preferred_ambience=[Ambience.cozy],
            allowlist={"kakao_1", "kakao_2"},
        )
    )

    assert [x.candidate.place_id for x in reranked] == ["kakao_1", "kakao_2"]
    assert reason_map == {}