from __future__ import annotations

import asyncio
from datetime import timedelta

import httpx
import pytest
from aiobreaker import CircuitBreaker, CircuitBreakerError

from app.clients.kakao_client import KakaoClient, KakaoTransientError


def test_search_places_retries_on_timeout(monkeypatch):
    client = KakaoClient()
    attempts = {"n": 0}

    async def fake_request_once(query: str, size: int):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise httpx.TimeoutException("timeout")
        return [{"id": "123"}]

    monkeypatch.setattr(client, "_request_once", fake_request_once)

    docs = asyncio.run(client.search_places("성수 카페", size=5))
    assert attempts["n"] == 2
    assert docs == [{"id": "123"}]


def test_search_places_circuit_breaker_opens_on_consecutive_failures(monkeypatch):
    client = KakaoClient()

    # 테스트를 위해 빨리 open 되도록 조정
    client.breaker = CircuitBreaker(
        fail_max=2,
        timeout_duration=timedelta(seconds=60),
    )

    async def always_fail(query: str, size: int):
        raise KakaoTransientError("forced 5xx")

    monkeypatch.setattr(client, "_search_with_retry", always_fail)

    with pytest.raises(KakaoTransientError):
        asyncio.run(client.search_places("성수 카페", size=5))

    with pytest.raises(CircuitBreakerError):
        asyncio.run(client.search_places("성수 카페", size=5))