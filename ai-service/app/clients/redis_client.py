from __future__ import annotations

from redis.asyncio import ConnectionPool, Redis

from app.core.config import get_settings

_pool: ConnectionPool | None = None
_client: Redis | None = None


def get_redis() -> Redis:
    """
    Redis 클라이언트 싱글턴.
    - 연결 풀 재사용으로 요청당 재연결 비용을 줄입니다.
    - 타임아웃을 명시해 장애 시 빠르게 실패합니다.
    """
    global _pool, _client

    if _client is not None:
        return _client

    settings = get_settings()
    _pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        decode_responses=True,        # str 반환
        socket_connect_timeout=1.0,   # 연결 timeout
        socket_timeout=2.0,           # read/write timeout
        retry_on_timeout=True,
    )
    _client = Redis(connection_pool=_pool)
    return _client