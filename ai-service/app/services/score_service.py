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
    점수:
    - base_score = 0.5
    - preferred_ambience 매칭 +0.2
    - feasibility penalty 가산
    - final_score는 0~1 clamp
    confidence:
    - final_score와 분리
    - ambience 추정 evidence 개수 기반
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
            inferred_tag, evidence_count = self._infer_ambience_tag_with_evidence(c)
            # 3. 가산점 계산: 사용자가 좋아하는 분위기랑 일치하면 0.2점 보너스!
            bonus = 0.2 if inferred_tag.value in preferred_tags else 0.0
            
            # 4. 점수 합산 로직 (수식 참고)
            # 기본 점수 0.5 + 취향 보너스 + 이동 페널티(음수)
            raw = 0.5 + bonus + c.penalty_score
            
            
            # 5. Clamp 처리: 점수가 0보다 작아지거나 1보다 커지지 않게 가둡니다.
            final_score = max(0.0, min(1.0, round(raw, 3)))

            # confidence는 evidence 중심으로 계산 (score와 분리)
            # evidence 0 -> 0.35, 1 -> 0.50, 2 -> 0.65 ...
            confidence_raw = 0.35 + (0.15 * evidence_count)
            if inferred_tag.value in preferred_tags:
                confidence_raw += 0.05
            confidence = max(0.0, min(1.0, round(confidence_raw, 3)))
            
            scored.append(
                ScoredCandidate(
                    candidate=c,
                    final_score=final_score,
                    confidence=final_score,  # MVP에서는 score와 동일하게 시작
                    ambience_tag=inferred_tag,
                )
            )

        return scored

    # 분위기 추론 엔진
    @staticmethod
    def _infer_ambience_tag_with_evidence(c: FeasibleCandidate) -> tuple[AmbienceTag, int]:
        text_chunks: list[str] = []
        if c.category_name:
            text_chunks.append(c.category_name.lower())
        if c.keywords:
            text_chunks.extend(k.lower() for k in c.keywords)
        haystack = " ".join(text_chunks)
        evidence: dict[AmbienceTag, int] = {
            AmbienceTag.cozy: 0,
            AmbienceTag.lively: 0,
            AmbienceTag.quiet: 0,
            AmbienceTag.work_friendly: 0,
        }
        cozy_tokens = {"카페", "디저트", "베이커리", "브런치", "감성", "cozy"}
        lively_tokens = {"술집", "펍", "클럽", "시장", "놀이", "액티비티", "lively"}
        quiet_tokens = {"서점", "갤러리", "조용", "한적", "quiet"}
        work_tokens = {"스터디", "코워킹", "와이파이", "wifi", "콘센트", "work"}
        for t in cozy_tokens:
            if t in haystack:
                evidence[AmbienceTag.cozy] += 1 
        for t in lively_tokens:
            if t in haystack:
                evidence[AmbienceTag.lively] += 1 # 오래 머물면 활동적인 곳일 가능성 +1
        for t in quiet_tokens:
            if t in haystack:
                evidence[AmbienceTag.quiet] += 1
        for t in work_tokens:
            if t in haystack:
                evidence[AmbienceTag.work_friendly] += 1
        # 기존 휴리스틱(체류/이동)도 약한 단서로 반영
        if c.stay_minutes >= 120:
            evidence[AmbienceTag.lively] += 1
        if c.travel_minutes <= 15:
            evidence[AmbienceTag.cozy] += 1
        best_tag = AmbienceTag.unknown
        best_score = 0
        for tag, cnt in evidence.items():
            if cnt > best_score:
                best_tag = tag
                best_score = cnt
        if best_score == 0:
            return AmbienceTag.unknown, 0
        return best_tag, best_score