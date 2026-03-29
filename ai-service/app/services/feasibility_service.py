from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from turtle import stamp
from typing import Any

from app.models.schemas import TimeSlot
from app.services.retrieve_service import CandidatePlace

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
# 슬롯 대표 시간(분 단위). 영업시간 판정에 사용.
_SLOT_MINUTE_OF_DAY: dict[TimeSlot, int] = {
    TimeSlot.breakfast: 8 * 60,
    TimeSlot.lunch: 12 * 60 + 30,
    TimeSlot.cafe: 15 * 60,
    TimeSlot.activity: 16 * 60,
    TimeSlot.dinner: 19 * 60,
    TimeSlot.dessert: 21 * 60,
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
    category_name: str = ""
    keywords: list[str] | None = None


class FeasibilityService:
    """
    규칙:
    - 이동시간 > 60분: 제거
    - 30~60분: 페널티 -0.15
    - 영업정보로 닫힘 확실: 제거
    - 영업정보 애매/부족: 제거 대신 penalty -0.05
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
            
            accepted_in_slot: list[CandidatePlace] = []
            
            for c in slot_candidates:
                travel = 0 if prev_ref is None else self._estimate_travel_minutes(prev_ref.lat, prev_ref.lng, c.lat, c.lng)
                if travel > 60:
                    continue
                # [필터링 규칙] 이동 시간이 1시간(60분) 초과면 아예 리스트에 넣지 않습니다. (제거)
                
                # [감점 규칙] 이동 시간이 30분~60분 사이면 -0.15점 페널티를 줍니다.
                penalty = -0.15 if 30 < travel <= 60 else 0.0
                
                # 영업 판정: True/False/None
                open_state = self._compute_open_state(c.business_info, slot)
                if open_state is False:
                    # 닫힘 확실하면 제거
                    continue
                if open_state is None:
                    # 애매하면 제거하지 않고 penalty 부여
                    penalty += -0.05
                    
                
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
                        penalty_score=round(penalty, 3),
                        open_at=open_state,
                        category_name=c.category_name,
                        keywords=c.keywords or [],
                    )
                )
                accepted_in_slot.append(c)

             # 다음 슬롯 거리 계산 기준점 
            if accepted_in_slot:
                prev_ref = accepted_in_slot[0]
            else:
                prev_ref = slot_candidates[0]

        return output
    
    @staticmethod
    def _compute_open_state(business_info: dict[str, Any] | None, slot: TimeSlot) -> bool | None:
        """
        반환값:
        - True  : 열림
        - False : 닫힘(확실)
        - None  : 판정불가(애매)
        """
        if not business_info:
            return None
        
         # 1) open_now 같은 명시 플래그 우선
        if "open_now" in business_info:
            value = business_info.get("open_now")
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"true", "open", "y", "yes", "1"}:
                    return True
                if lowered in {"false", "closed", "n", "no", "0"}:
                    return False

         # 2) closed/holiday 힌트 (닫힘 단서만 강하게 반영)
        closed = business_info.get("closed")
        holiday = business_info.get("holiday")
        if isinstance(closed, bool) and closed:
            return False
        if isinstance(holiday, bool) and holiday:
            return False
        
        # 3) business_hours(예: "10:00-22:00") 파싱
        # 실제 응답 포맷이 일정치 않을 수 있어, 가능한 범위만 처리
        raw_hours = business_info.get("business_hours") or business_info.get("bizhour")
        if isinstance(raw_hours, str):
            parsed = FeasibilityService._parse_hour_range(raw_hours)
            if parsed is None:
                return None
            start_m, end_m = parsed
            target = _SLOT_MINUTE_OF_DAY[slot]
            return FeasibilityService._is_in_range(target, start_m, end_m)
        
        return None
    
   
    @staticmethod
    def _parse_hour_range(raw: str) -> tuple[int, int] | None:
        # 예: "10:00-22:00", "11:30 ~ 21:00"
        cleaned = raw.replace("~", "-").replace(" ", "")
        if "-" not in cleaned:
            return None
        left, right = cleaned.split("-", 1)
        start_m = FeasibilityService._parse_hhmm(left)
        end_m = FeasibilityService._parse_hhmm(right)
        if start_m is None or end_m is None:
            return None
        return (start_m, end_m)
    
    @staticmethod
    def _parse_hhmm(text: str) -> int | None:
        if ":" not in text:
            return None
        hh, mm = text.split(":", 1)
        if not (hh.isdigit() and mm.isdigit()):
            return None
        h = int(hh)
        m = int(mm)
        if h < 0 or h > 24 or m < 0 or m > 59:
            return None
        return h * 60 + m
    
    @staticmethod
    def _is_in_range(target: int, start_m: int, end_m: int) -> bool:
        # 영업 종료가 자정 넘김(예: 18:00-02:00) 케이스 처리
        if start_m <= end_m:
            return start_m <= target <= end_m
        return target >= start_m or target <= end_m
    
    @staticmethod
    def _estimate_travel_minutes(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
        km = _haversine_km(lat1, lng1, lat2, lng2)
        minutes = (km / 20.0) * 60.0
        return max(1, int(round(minutes)))
    
    @staticmethod
    def _estimate_travel_minutes(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
        # Haversine 거리(km) -> 도시 이동 평균속도 20km/h 가정
        # 직선 거리(km)를 구합니다.
        km = _haversine_km(lat1, lng1, lat2, lng2)
        
        # 서울 시내 평균 속도 20km/h 가정: (거리 / 속력) * 60분
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