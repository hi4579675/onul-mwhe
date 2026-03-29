from __future__ import annotations

from app.models.schemas import Ambience, TimeSlot
from app.services.feasibility_service import FeasibleCandidate
from app.services.score_service import ScoreService


def _candidate(
    *,
    place_id: str = "kakao_1",
    slot: TimeSlot = TimeSlot.lunch,
    travel_minutes: int = 10,
    stay_minutes: int = 60,
    penalty_score: float = 0.0,
) -> FeasibleCandidate:
    return FeasibleCandidate(
        place_id=place_id,
        name="test_place",
        slot=slot,
        lat=37.5,
        lng=127.0,
        travel_minutes=travel_minutes,
        stay_minutes=stay_minutes,
        penalty_score=penalty_score,
        open_at=True,
    )


def test_score_returns_empty_on_no_candidates():
    service = ScoreService()
    scored = service.score([], [Ambience.cozy])
    assert scored == []


def test_score_applies_preference_bonus():
    service = ScoreService()
    # travel <= 15 -> inferred_tag = cozy
    c = _candidate(travel_minutes=10, stay_minutes=60, penalty_score=0.0)

    scored = service.score([c], [Ambience.cozy])

    assert len(scored) == 1
    assert scored[0].ambience_tag.value == "cozy"
    # 0.5 + 0.2 + 0.0
    assert scored[0].final_score == 0.7
    assert scored[0].confidence == 0.7


def test_score_clamps_lower_bound():
    service = ScoreService()
    c = _candidate(travel_minutes=40, stay_minutes=60, penalty_score=-1.0)  # 0.5 -1.0 = -0.5 -> 0.0 clamp

    scored = service.score([c], [Ambience.quiet])

    assert scored[0].final_score == 0.0
    assert scored[0].confidence == 0.0


def test_score_clamps_upper_bound():
    service = ScoreService()
    # cozy 매칭 + 큰 양수 penalty로 1.0 상한 확인
    c = _candidate(travel_minutes=5, stay_minutes=60, penalty_score=0.8)  # 0.5 + 0.2 + 0.8 = 1.5 -> 1.0

    scored = service.score([c], [Ambience.cozy])

    assert scored[0].final_score == 1.0
    assert scored[0].confidence == 1.0