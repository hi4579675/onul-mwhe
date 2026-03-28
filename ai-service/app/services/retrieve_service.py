from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.clients.kakao_client import KakaoClient
from app.core.config import get_settings
from app.models.schemas import TimeSlot


@dataclass # 자바의 @Date나 class
class CandidatePlace:
    place_id: str
    name: str
    slot: TimeSlot
    lat: float # 위도
    lng: float # 경도


_SLOT_QUERY_SUFFIX = {
    TimeSlot.breakfast: "아침 식사",
    TimeSlot.lunch: "점심 맛집",
    TimeSlot.cafe: "카페",
    TimeSlot.activity: "놀거리",
    TimeSlot.dinner: "저녁 맛집",
    TimeSlot.dessert: "디저트",
}


class RetrieveService:
    def __init__(self) -> None:
        self.client = KakaoClient()
        self.max_n = get_settings().MAX_CANDIDATES_PER_CATEGORY

    async def retrieve(self, region: str, slots: list[TimeSlot]) -> list[CandidatePlace]:
        # 1. 아침, 점심, 카페 등 각 슬롯별로 할 일 목록을 만든다
        tasks = [self._retrieve_for_slot(region, slot) for slot in slots]
        # 2. [asyncio.gather] - 여러 개의 API 호출을 동시에(병렬로) 날린다.
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # 각 슬롯별 결과를 하나의 리스트로 병합한다.
        merged: list[CandidatePlace] = []
        for r in results:
            if isinstance(r, Exception):
                continue
            merged.extend(r)
        return merged

    async def _retrieve_for_slot(self, region: str, slot: TimeSlot) -> list[CandidatePlace]:
        # 3. 쿼리 생성: 예) "성수 점심 맛집", "성수 카페"
        q = f"{region} {_SLOT_QUERY_SUFFIX.get(slot, '맛집')}"
        docs = await self.client.search_places(q, size=self.max_n)
        # 4. KakaoClient를 통해 실제 데이터 수집
        out: list[CandidatePlace] = []
        for d in docs[: self.max_n]:
            x = d.get("x")
            y = d.get("y")
            if not x or not y:
                continue
            out.append(
                CandidatePlace(
                    place_id=f"kakao_{d.get('id', 'unknown')}",
                    name=d.get("place_name", "unknown"),
                    slot=slot,
                    lat=float(y),
                    lng=float(x),
                )
            )
        return out