from __future__ import annotations
import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from typing import Any

from app.clients.kakao_client import KakaoClient
from app.clients.redis_client import get_redis
from app.core.config import get_settings
from app.models.schemas import TimeSlot

logger = logging.getLogger(__name__)


@dataclass # 자바의 @Date나 class
class CandidatePlace:
    place_id: str
    name: str
    slot: TimeSlot
    lat: float # 위도
    lng: float # 경도
    category_name: str = ""
    keywords: list[str] | None = None
    business_info: dict[str, Any] | None = None


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
        settings = get_settings()
        self.client = KakaoClient()
        self.redis = get_redis()
        self.max_n = settings.MAX_CANDIDATES_PER_CATEGORY
        self.ttl = settings.TTL_CANDIDATES  # 요구사항: 3600

    async def retrieve(self, region: str, slots: list[TimeSlot]) -> list[CandidatePlace]:
        # 각 슬롯(점심, 카페 등)별로 비동기 작업 리스트 생성
        tasks = [self._retrieve_for_slot(region, slot) for slot in slots]
        # 2. [asyncio.gather] - 여러 개의 API 호출을 동시에(병렬로) 날린다.
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # 각 슬롯별 결과를 하나의 리스트로 병합한다.
        merged: list[CandidatePlace] = []
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Retrieve failed: {r}")
                continue
            merged.extend(r)
        return merged

    async def _retrieve_for_slot(self, region: str, slot: TimeSlot) -> list[CandidatePlace]:
         # 1) 캐시 키 생성 (예: place:candidates:v1:성수동:lunch)
        cache_key = self._cache_key(region, slot)
        
         # 2) [Cache-Aside] 먼저 Redis에서 확인
        try: 
            cached = await self.redis.get(cache_key)
            if cached:
                rows = json.loads(cached) # JSON 문자열을 리스트로 파싱
                # 파싱된 데이터를 다시 객체(CandidatePlace)로 변환해서 반환
                return [self._candidate_from_cache(row) for row in rows]
        except Exception as e:
           # Redis가 죽어도 서비스는 돌아가야 하므로 경고 로그만 남김 (Soft Fail)
            logger.error(f"Redis get failed: {e}")
            cached = None
            
        # 3) 캐시 미스(Miss) 시 카카오 API 호출
        #  쿼리 생성: 예) "성수 점심 맛집", "성수 카페"
        q = f"{region} {_SLOT_QUERY_SUFFIX.get(slot, '맛집')}"
        docs = await self.client.search_places(q, size=self.max_n)
        
        # KakaoClient를 통해 실제 데이터 수집
        out: list[CandidatePlace] = []
        for d in docs[: self.max_n]:
            x = d.get("x")
            y = d.get("y")
            if not x or not y:
                continue
            
            # 데이터를 가공해서 리스트에 담음    
            out.append(
                CandidatePlace(
                    place_id=f"kakao_{d.get('id', 'unknown')}",
                    name=d.get("place_name", "unknown"),
                    slot=slot,
                    lat=float(y),
                    lng=float(x),
                    category_name=d.get("category_name", ""),
                    keywords=self._extract_keywords(d),
                    business_info=self._extract_business_info(d),
                )
            )
            
        # 4) 수집된 결과를 Redis에 저장 (다음 번에는 API 안 부르게!)
        try:
          # 객체 리스트를 JSON 저장 가능한 딕셔너리 리스트로 변환
          payload = [self._candidate_to_cache(item) for item in out]
          # [setex] 키 저장 + 만료시간(TTL) 설정
          await self.redis.setex(cache_key, self.ttl, json.dumps(payload, ensure_ascii=False))
        except Exception as e:
          logger.warning("retrieve.cache_write_failed key=%s error=%s", cache_key, e)
        
        return out

    @staticmethod
    def _cache_key(region: str, slot: TimeSlot) -> str:
        # 공백 제거 및 소문자화하여 일관된 키 생성
        # 요구사항 키 포맷: place:candidates:v1:{region}:{slot}
        normalized_region = region.strip().lower()
        return f"place:candidates:v1:{normalized_region}:{slot.value}"
    
    @staticmethod
    def _extract_keywords(doc: dict[str, Any]) -> list[str]:
        # 장소명과 카테고리명을 쪼개서 키워드 집합을 만듭니다.
        # 예: "일식 > 초밥" -> ["일식", "초밥"]
        bag: list[str] = []
        for raw in [doc.get("place_name", ""), doc.get("category_name", "")]:
            if not raw:
                continue
            tokens = [t.strip().lower() for t in raw.replace(">", " ").replace("/", " ").split()]
            bag.extend([t for t in tokens if t])
        return list(dict.fromkeys(bag))  # 중복 제거 + 순서 유지
    
    @staticmethod
    def _extract_business_info(doc: dict[str, Any]) -> dict[str, Any] | None:
        # 카카오 응답 데이터 중 영업 관련 필드만 쏙 골라냅니다.
        info: dict[str, Any] = {}
        for key in ["open_now", "business_hours", "bizhour", "holiday", "closed"]:
            if key in doc:
                info[key] = doc.get(key)
        return info or None
    
    @staticmethod
    def _candidate_to_cache(item: CandidatePlace) -> dict[str, Any]:
        # 객체를 딕셔너리로 변환 (asdict)
        row = asdict(item)
        # Enum 객체는 JSON에 안 담기므로 문자열(value)로 바꿔줍니다.
        row["slot"] = item.slot.value
        return row
    
    @staticmethod
    def _candidate_from_cache(row: dict[str, Any]) -> CandidatePlace:
        # 딕셔너리 데이터를 다시 CandidatePlace 객체로 조립합니다.
        return CandidatePlace(
            place_id=row["place_id"],
            name=row["name"],
            slot=TimeSlot(row["slot"]),
            lat=float(row["lat"]),
            lng=float(row["lng"]),
            category_name=row.get("category_name", ""),
            keywords=row.get("keywords") or [],
            business_info=row.get("business_info"),
        )