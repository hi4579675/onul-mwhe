from __future__ import annotations

import asyncio

from app.models.schemas import TimeSlot
from app.services.retrieve_service import CandidatePlace, RetrieveService


def test_retrieve_for_slot_maps_kakao_docs(monkeypatch):
    service = RetrieveService()

    async def fake_search_places(query: str, size: int = 10):
        return [
            {"id": "123", "place_name": "A카페", "x": "127.11", "y": "37.55"},
            {"id": "124", "place_name": "좌표없음", "x": None, "y": "37.56"},  # 필터됨
            {"id": "125", "place_name": "B카페", "x": "127.12", "y": "37.56"},
        ]

    monkeypatch.setattr(service.client, "search_places", fake_search_places)

    results = asyncio.run(service._retrieve_for_slot("성수", TimeSlot.cafe))

    assert len(results) == 2
    assert results[0].place_id == "kakao_123"
    assert results[0].name == "A카페"
    assert results[0].slot == TimeSlot.cafe
    assert isinstance(results[0].lat, float)
    assert isinstance(results[0].lng, float)


def test_retrieve_merges_results_and_skips_exceptions(monkeypatch):
    service = RetrieveService()

    async def fake_retrieve_for_slot(region: str, slot: TimeSlot):
        if slot == TimeSlot.cafe:
            raise RuntimeError("forced failure")
        return [
            CandidatePlace(
                place_id=f"kakao_{slot.value}",
                name=f"{slot.value}_place",
                slot=slot,
                lat=37.5,
                lng=127.0,
            )
        ]

    monkeypatch.setattr(service, "_retrieve_for_slot", fake_retrieve_for_slot)

    results = asyncio.run(service.retrieve("성수", [TimeSlot.lunch, TimeSlot.cafe, TimeSlot.dinner]))

    # cafe는 예외로 누락되고, lunch/dinner만 병합됨
    assert len(results) == 2
    assert {r.slot for r in results} == {TimeSlot.lunch, TimeSlot.dinner}