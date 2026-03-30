from __future__ import annotations

from app.models.schemas import AllergyType, TimeSlot
from app.services.dietary_filter_service import DietaryFilterService
from app.services.feasibility_service import FeasibleCandidate


def _candidate(name: str, category_name: str, keywords: list[str]) -> FeasibleCandidate:
    return FeasibleCandidate(
        place_id="kakao_1",
        name=name,
        slot=TimeSlot.lunch,
        lat=37.5,
        lng=127.0,
        travel_minutes=10,
        stay_minutes=60,
        penalty_score=0.0,
        open_at=True,
        category_name=category_name,
        keywords=keywords,
    )


def test_allergy_filter_removes_shellfish_candidate():
    service = DietaryFilterService()
    candidates = [_candidate("새우맛집", "한식", ["새우", "점심"])]

    out = service.apply(candidates, allergies=[AllergyType.SHELLFISH], vegan=False)

    assert out == []


def test_vegan_filter_removes_meat_candidate():
    service = DietaryFilterService()
    candidates = [_candidate("정육식당", "고기", ["삼겹살"])]

    out = service.apply(candidates, allergies=[AllergyType.NONE], vegan=True)

    assert out == []


def test_filter_keeps_safe_candidate():
    service = DietaryFilterService()
    candidates = [_candidate("비건카페", "카페", ["비건", "샐러드"])]

    out = service.apply(candidates, allergies=[AllergyType.PEANUT], vegan=True)

    assert len(out) == 1
