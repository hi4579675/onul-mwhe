from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt

from app.models.schemas import TimeSlot
from app.services.retrieve_service import CandidatePlace

# 슬롯별 기본 체류시간(분)
_STAY_MINUTES_BY_SLOT: dict[TimeSlot, int] = {
    TimeSlot.breakfast: 60,
    TimeSlot.lunch: 90,
    TimeSlot.cafe: 60,
    TimeSlot.activity: 120,
    TimeSlot.dinner: 90,
    TimeSlot.dessert: 60,
}

_SLOT_ORDER: dict[TimeSlot, int] = {
    TimeSlot.breakfast: 1,
    TimeSlot.lunch: 2,
    TimeSlot.cafe: 3,
    TimeSlot.activity: 4,
    TimeSlot.dinner: 5,
    TimeSlot.dessert: 6,
}


@dataclass
class FeasibleCandidate:
    place_id: str
    name: str
    slot: TimeSlot
    lat: float
    lng: float
    travel_minutes: int   # 이전 장소에서 여기까지 오는 데 걸리는 시간
    stay_minutes: int     # 이 장소에서 머무는 시간
    penalty_score: float  # 이동 거리에 따른 감점 점수 (0 또는 -0.15)
    open_at: bool = True  # 영업 여부 (기본값 True)


class FeasibilityService:
    """
    MVP 규칙:
    - 이동시간 > 60분: 제거
    - 30~60분: 페널티 -0.15
    - <=30분: 페널티 0
    - 영업정보 미보유 시 open_at=True로 간주
    """

    def apply(self, candidates: list[CandidatePlace], requested_slots: list[TimeSlot]) -> list[FeasibleCandidate]:
        if not candidates:
            return []
        # 1. 데이터를 슬롯별로 그룹화합니다. (Map<TimeSlot, List<Candidate>> 형태)
        by_slot: dict[TimeSlot, list[CandidatePlace]] = {}
        for c in candidates:
            by_slot.setdefault(c.slot, []).append(c) # 리스트가 없으면 만들고 추가

        # 2. 사용자가 요청한 슬롯들을 시간 순서(아침->점심->저녁)대로 정렬합니다.
        ordered_slots = sorted(
            [s for s in requested_slots if s in by_slot],
            key=lambda s: _SLOT_ORDER[s],
        )

        prev_ref: CandidatePlace | None = None # 이전 장소의 위치를 저장할 변수
        output: list[FeasibleCandidate] = []   # 최종 결과 리스트

        # 3. 정렬된 슬롯 순서대로 반복문을 돌립니다. (예: 점심 -> 카페 -> 저녁)
        for slot in ordered_slots:
            # 이전 장소가 없다면(첫 번째 일정) 이동시간은 0분입니다.
            # 있다면 이전 위도/경도와 현재 위도/경도로 이동 시간을 계산합니다.
            slot_candidates = by_slot.get(slot, [])
            if not slot_candidates:
                continue

            for c in slot_candidates:
                travel = 0 if prev_ref is None else self._estimate_travel_minutes(prev_ref.lat, prev_ref.lng, c.lat, c.lng)
                # [필터링 규칙] 이동 시간이 1시간(60분) 초과면 아예 리스트에 넣지 않습니다. (제거)
                if travel > 60:
                    continue  # 제거
                # [감점 규칙] 이동 시간이 30분~60분 사이면 -0.15점 페널티를 줍니다.
                penalty = -0.15 if 30 < travel <= 60 else 0.0
                
                # 5. 계산된 정보를 담아 FeasibleCandidate 객체를 생성합니다.
                output.append(
                    FeasibleCandidate(
                        place_id=c.place_id,
                        name=c.name,
                        slot=c.slot,
                        lat=c.lat,
                        lng=c.lng,
                        travel_minutes=travel,
                        stay_minutes=_STAY_MINUTES_BY_SLOT.get(c.slot, 60),
                        penalty_score=penalty,
                        open_at=True,
                    )
                )

            # 6. [중요] 다음 슬롯의 이동 시간을 계산하기 위해, 현재 슬롯의 '첫 번째' 후보를 기준점으로 잡습니다.
            # MVP 단계라 단순하게 첫 번째 후보를 기준으로 다음 거리를 계산하는 방식을 택했습니다.
            prev_ref = slot_candidates[0]

        return output

    @staticmethod
    def _estimate_travel_minutes(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
        # Haversine 거리(km) -> 도시 이동 평균속도 20km/h 가정
        # 직선 거리(km)를 구합니다.
        km = _haversine_km(lat1, lng1, lat2, lng2)
        
        # 서울 시내 평균 속도 20km/h 가정: (거리 / 속력) * 60분
        minutes = (km / 20.0) * 60.0
        
        minutes = (km / 20.0) * 60.0
        return max(1, int(round(minutes)))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """위도/경도로 지구 표면의 거리 구하기"""
    r = 6371.0  # 지구 반지름(km)
    d_lat = radians(lat2 - lat1)  # 라디안 단위로 변환
    d_lon = radians(lon2 - lon1)
    
    # 하버사인 공식 (구형 삼각법)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c # 최종 거리(km)