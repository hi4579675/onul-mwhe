from __future__ import annotations

from app.models.schemas import TimeSlot
from app.services.feasibility_service import FeasibilityService
from app.services.retrieve_service import CandidatePlace


def _c(
    slot: TimeSlot,
    *,
    lat: float = 37.55,
    lng: float = 127.05,
    business_info=None,
):
    return CandidatePlace(
        place_id=f"kakao_{slot.value}",
        name=f"{slot.value}_place",
        slot=slot,
        lat=lat,
        lng=lng,
        category_name="카페",
        keywords=["cozy"],
        business_info=business_info,
    )


def test_open_state_with_open_now_true():
    service = FeasibilityService()
    res = service._compute_open_state({"open_now": True}, TimeSlot.lunch)
    assert res is True


def test_open_state_with_closed_true():
    service = FeasibilityService()
    res = service._compute_open_state({"closed": True}, TimeSlot.dinner)
    assert res is False


def test_business_hours_parsing_simple_range():
    service = FeasibilityService()
    res = service._compute_open_state({"business_hours": "10:00-22:00"}, TimeSlot.dinner)
    assert res is True  # 19:00대는 열림


def test_business_hours_parsing_cross_midnight():
    service = FeasibilityService()
    res = service._compute_open_state({"business_hours": "18:00-02:00"}, TimeSlot.dessert)
    assert res is True  # 21:00대 열림


def test_apply_removes_clearly_closed_place():
    service = FeasibilityService()
    candidates = [_c(TimeSlot.lunch, business_info={"open_now": False})]
    out = service.apply(candidates, [TimeSlot.lunch])
    assert out == []