from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import httpx
from aiobreaker import CircuitBreaker, CircuitBreakerError
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings

logger = logging.getLogger(__name__)
class KakaoTransientError(RuntimeError):
    """재시도 가능한 오류(5xx, 일시 네트워크 장애 등)."""
class KakaoPermanentError(RuntimeError):
    """재시도 불필요한 오류(주로 4xx)."""

class KakaoClient:
    def __init__(self) -> None:
        settings = get_settings()
        
        self.base_url = settings.KAKAO_BASE_URL
        # 카카오가 요구하는 "KakaoAK [키]" 형식으로 헤더 준비
        self.headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}
        
        self.timeout = httpx.Timeout(
            timeout=settings.KAKAO_TIMEOUT_SECONDS,
            connect=settings.KAKAO_CONNECT_TIMEOUT_SECONDS,
        )
        
        self.retry_max_attempts = settings.KAKAO_RETRY_MAX_ATTEMPTS
        self.retry_min_wait = settings.KAKAO_RETRY_MIN_WAIT_SECONDS
        self.retry_max_wait = settings.KAKAO_RETRY_MAX_WAIT_SECONDS
        
        # 4xx(permanent)는 breaker 실패 카운트에서 제외
        # 서버가 죽었는데 계속 요청을 보내면 우리 서버 자원만 낭비되고 대기시간만 길어지니 차단하는 것 
        self.breaker = CircuitBreaker(
            fail_max=settings.KAKAO_CB_FAIL_MAX, # N번 실패하면 차단
            timeout_duration=timedelta(seconds=settings.KAKAO_CB_RESET_TIMEOUT_SECONDS),
            exclude=[KakaoPermanentError], # 4xx 에러는 우리 잘못이니 차단 안함
        )


    async def search_places(self, query: str, size: int = 10) -> list[dict[str, Any]]:
      # 비동기(Non-blocking) 처리 : 카카오 서버가 답장을 줄 때까지 스레드가 멍하니 기다리는 게 아니라, 다른 일을 할 수 있게 해줌
        # 통신이 끝나면 클라이언트를 자동으로 닫아줘
        try:
            return await self.breaker.call_async(self._search_with_retry, query, size)
        except CircuitBreakerError:
            logger.error(
                "event=kakao.search_places.failed reason=circuit_open query=%s size=%d",
                query,
                size,
            )
            raise
        except Exception as exc:
            logger.error(
                "event=kakao.search_places.failed reason=%s query=%s size=%d detail=%s",
                self._classify_error(exc),
                query,
                size,
                str(exc),
            )
            raise
    async def _search_with_retry(self, query: str, size: int) -> list[dict[str, Any]]:
        # Exponential backoff: 네트워크 통신이나 분산 시스템에서 재시도를 할 때 기다리는 시간을 기하급수적으로 늘려가는 전략
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retry_max_attempts), # 최대 재시도 횟수
            wait=wait_exponential(min=self.retry_min_wait, max=self.retry_max_wait), # 재시도 간격 증가 1초 쉬고,, 2초쉬고,,,또 안되면 4초 쉬고
            retry=retry_if_exception_type(
                (KakaoTransientError, httpx.TimeoutException, httpx.TransportError) # 재시도 가능한 오류
            ),
            reraise=True,
        )
        async for attempt in retryer:
            with attempt:
                attempt_no = attempt.retry_state.attempt_number
                try:
                    return await self._request_once(query, size)
                except Exception as exc:
                    logger.warning(
                        "event=kakao.search_places.retry attempt=%d reason=%s query=%s size=%d detail=%s",
                        attempt_no,
                        self._classify_error(exc),
                        query,
                        size,
                        str(exc),
                    )
                    raise
        return []
    async def _request_once(self, query: str, size: int) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
        ) as client:
            try:
                res = await client.get(
                    "/v2/local/search/keyword.json",
                    params={"query": query, "size": size},
                )
            except httpx.TimeoutException:
                logger.warning(
                    "event=kakao.search_places.error reason=timeout query=%s size=%d",
                    query,
                    size,
                )
                raise
            except httpx.TransportError:
                logger.warning(
                    "event=kakao.search_places.error reason=network query=%s size=%d",
                    query,
                    size,
                )
                raise
        status = res.status_code
        if 500 <= status < 600:
            raise KakaoTransientError(f"http_5xx status={status}")
        if 400 <= status < 500:
            raise KakaoPermanentError(f"http_4xx status={status}")
        res.raise_for_status()
        data = res.json()
        return data.get("documents", [])
    @staticmethod
    def _classify_error(exc: Exception) -> str:
        if isinstance(exc, CircuitBreakerError):
            return "circuit_open"
        if isinstance(exc, httpx.TimeoutException):
            return "timeout"
        if isinstance(exc, httpx.TransportError):
            return "network"
        if isinstance(exc, KakaoTransientError):
            return "http_5xx"
        if isinstance(exc, KakaoPermanentError):
            return "http_4xx"
        return "unknown"
