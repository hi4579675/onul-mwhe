from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import Ambience, AmbienceTag
from app.services.feasibility_service import FeasibleCandidate


@dataclass
class ScoredCandidate:
    candidate: FeasibleCandidate # 이전 단계에서 넘어온 후보 정보
    final_score: float           # 최종 점수 (0.0 ~ 1.0)
    confidence: float            #이 추천을 얼마나 확신하는가
    ambience_tag: AmbienceTag    # 이 장소의 분위기 (추정치)


class ScoreService:
    """
    MVP 단순 점수:
    - base_score = 0.5
    - preferred_ambience 매칭 +0.2
    - feasibility penalty 가산 (음수)
    - 점수 범위 0.0 ~ 1.0 clamp
    """

    def score(
        self,
        feasible: list[FeasibleCandidate], 
        preferred_ambience: list[Ambience], # 사용자가 선호하는 분위기 리스트
    ) -> list[ScoredCandidate]:
        if not feasible:
            return []
        # 1. 사용자의 선호 태그를 Set으로 변환 (자바의 HashSet처럼 빠르게 검색하려고)
        preferred_tags = {p.value for p in preferred_ambience}
        scored: list[ScoredCandidate] = [] # 최종 결과 리스트

        for c in feasible:
          # 2. 이 장소의 분위기를 추측합니다. (아래 private 메서드 호출)
            inferred_tag = self._infer_ambience_tag(c)
            # 3. 가산점 계산: 사용자가 좋아하는 분위기랑 일치하면 0.2점 보너스!
            bonus = 0.2 if inferred_tag.value in preferred_tags else 0.0
            
            # 4. 점수 합산 로직 (수식 참고)
            # 기본 점수 0.5 + 취향 보너스 + 이동 페널티(음수)
            raw = 0.5 + bonus + c.penalty_score
            
            # 5. Clamp 처리: 점수가 0보다 작아지거나 1보다 커지지 않게 가둡니다.
            final_score = max(0.0, min(1.0, round(raw, 3)))

            scored.append(
                ScoredCandidate(
                    candidate=c,
                    final_score=final_score,
                    confidence=final_score,  # MVP에서는 score와 동일하게 시작
                    ambience_tag=inferred_tag,
                )
            )

        return scored

    @staticmethod
    def _infer_ambience_tag(c: FeasibleCandidate) -> AmbienceTag:
        # MVP 단계의 꼼수(Heuristic): 실제 데이터가 없으니 특징으로 추측합니다.
        # 120분 이상 머문다? -> "시끌벅적하고 활기찬(lively) 곳이겠군!" (예: 놀이시설)
        if c.stay_minutes >= 120:
            return AmbienceTag.lively
        # 이동 시간이 15분 이내다? -> "가까운 곳에 있는 편안한(cozy) 곳이군!"
        if c.travel_minutes <= 15:
            return AmbienceTag.cozy
        return AmbienceTag.unknown