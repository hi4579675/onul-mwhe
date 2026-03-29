from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import (
    AmbienceTag,
    PlanItem,
    RouteGenerateSuccessResponse,
    TimeSlot,
)


def _valid_payload() -> dict:
    return {
        "region": "성수",
        "timeslots": ["lunch", "cafe", "dinner"],
        "preferred_ambience": ["cozy", "quiet"],
        "food_type": ["한식"],
        "budget_level": "normal",
    }


def test_generate_route_success(monkeypatch):
    from app.api.routes import route as route_module

    class StubRouteService:
        async def generate(self, body, correlation_id):
            return RouteGenerateSuccessResponse(
                plan=[
                    PlanItem(
                        place_id="kakao_12345",
                        slot=TimeSlot.lunch,
                        order=1,
                        reason="테스트 추천",
                        confidence=0.8,
                        ambience_tag=AmbienceTag.cozy,
                    )
                ],
                fallback_used=False,
                unknown_count=0,
                correlation_id=correlation_id,
            )

    monkeypatch.setattr(route_module, "route_service", StubRouteService())

    client = TestClient(app)
    cid = "550e8400-e29b-41d4-a716-446655440000"

    res = client.post(
        "/api/v1/route/generate",
        headers={"X-Correlation-ID": cid},
        json=_valid_payload(),
    )

    assert res.status_code == 200
    data = res.json()
    assert data["fallback_used"] is False
    assert data["correlation_id"] == cid
    assert len(data["plan"]) == 1
    assert data["plan"][0]["place_id"] == "kakao_12345"


def test_generate_route_validation_duplicate_timeslots():
    client = TestClient(app)
    payload = _valid_payload()
    payload["timeslots"] = ["lunch", "lunch"]  # 중복

    res = client.post(
        "/api/v1/route/generate",
        headers={"X-Correlation-ID": "550e8400-e29b-41d4-a716-446655440000"},
        json=payload,
    )

    assert res.status_code == 422


def test_generate_route_validation_missing_header():
    client = TestClient(app)

    res = client.post(
        "/api/v1/route/generate",
        json=_valid_payload(),
    )

    assert res.status_code == 422
    detail = res.json()["detail"]
    assert any("X-Correlation-ID" in str(item.get("loc", [])) for item in detail)


def test_generate_route_fallback_on_exception(monkeypatch):
    from app.api.routes import route as route_module

    class FailingRouteService:
        async def generate(self, body, correlation_id):
            raise RuntimeError("forced failure")

    monkeypatch.setattr(route_module, "route_service", FailingRouteService())

    client = TestClient(app)
    cid = "550e8400-e29b-41d4-a716-446655440000"

    res = client.post(
        "/api/v1/route/generate",
        headers={"X-Correlation-ID": cid},
        json=_valid_payload(),
    )

    assert res.status_code == 200
    data = res.json()
    assert data["fallback_used"] is True
    assert data["plan"] == []
    assert data["unknown_count"] == 0
    assert data["correlation_id"] == cid
    
    