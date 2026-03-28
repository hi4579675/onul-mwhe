from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


class KakaoClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.KAKAO_BASE_URL
        # 카카오가 요구하는 "KakaoAK [키]" 형식으로 헤더 준비
        self.headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}
        self.timeout = settings.KAKAO_TIMEOUT_SECONDS

    async def search_places(self, query: str, size: int = 10) -> list[dict[str, Any]]:
      # 비동기(Non-blocking) 처리 : 카카오 서버가 답장을 줄 때까지 스레드가 멍하니 기다리는 게 아니라, 다른 일을 할 수 있게 해줌
        # 통신이 끝나면 클라이언트를 자동으로 닫아줘
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
        ) as client:
            res = await client.get(
                "/v2/local/search/keyword.json",
                params={"query": query, "size": size}, # ?query=성수동&size=10
            )
            res.raise_for_status()
            data = res.json() # 응답 바디를 JSON(Dict)으로 변환
            return data.get("documents", []) # 결과 리스트만 쏙 뽑아서 반환