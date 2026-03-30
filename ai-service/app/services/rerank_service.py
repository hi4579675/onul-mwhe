from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.models.schemas import Ambience, TimeSlot
from app.services.score_service import ScoredCandidate

logger = logging.getLogger(__name__)


class RerankService:
    """
    MVP:
    - 실제 LLM 연동 전 단계로, "LLM 출력 형태"를 흉내 낸 구조를 먼저 고정
    - allowlist(place_id) 검증으로 후보 외 ID를 차단
    """

    def __init__(self, model: str, timeout_seconds: float) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def rerank_slot_candidates(
        self,
        *,
        slot: TimeSlot,
        candidates: list[ScoredCandidate],
        region: str,
        preferred_ambience: list[Ambience],
        allowlist: set[str], # AI가 환각을 일으켜 가짜 ID를 만드는 걸 막는 방어
    ) -> tuple[list[ScoredCandidate], dict[str, str]]:
        if not candidates:
            return [], {}
        # 1. 실제 LLM(또는 MVP 함수)을 호출합니다.
        # asyncio.wait_for: 설정한 시간 내에 대답이 안오면 에러 발생
        try:
            llm_items = await asyncio.wait_for(
                self._call_llm_mvp(slot, candidates, region, preferred_ambience),
                timeout=self.timeout_seconds,
            )
        except Exception as e:
         # 2. [Fallback 로직]
            logger.warning(
                "event=rerank.failed reason=llm_error slot=%s model=%s error=%s",
                slot.value,
                self.model,
                e,
            )
            return candidates, {}

        # allowlist 검증 + 중복 제거
        ranked_ids: list[str] = []
        reason_by_place_id: dict[str, str] = {}

        for item in llm_items:
            pid = str(item.get("place_id", "")).strip()
            reason = str(item.get("reason", "")).strip()

            # 3. [보안/무결성 체크] 우리가 준 후보 목록(allowlist)에 없는 ID를 AI가 지어냈다면?
            # 과감히 무시합니다. (Hallucination 방지)
            if not pid or pid not in allowlist:
                logger.warning(
                    "event=rerank.invalid_place_id slot=%s place_id=%s",
                    slot.value,
                    pid,
                )
                continue
            # 4. [중복 방지] 같은 ID가 두 번 들어오면 처음 것만 인정합니다.
            if pid in ranked_ids:
                continue

            ranked_ids.append(pid)
            if reason:
                reason_by_place_id[pid] = reason

        # 5. [데이터 유실 방지] LLM이 누락한 후보는 기존 순서대로 뒤에 유지
        for c in candidates:
            pid = c.candidate.place_id
            if pid not in ranked_ids:
                ranked_ids.append(pid)

        by_place_id: dict[str, ScoredCandidate] = {}
        for c in candidates:
            # 동일 place_id 중복 시 첫 항목 우선
            by_place_id.setdefault(c.candidate.place_id, c)

        reranked = [by_place_id[pid] for pid in ranked_ids if pid in by_place_id]
        return reranked, reason_by_place_id

    async def _call_llm_mvp(
        self,
        slot: TimeSlot,
        candidates: list[ScoredCandidate],
        region: str,
        preferred_ambience: list[Ambience],
    ) -> list[dict[str, Any]]:
        """
        TODO: 실제 LLM API 호출로 교체.
        현재는 결정론적 MVP 정렬(점수+confidence) + reason 생성.
        """
        _ = (slot, region, preferred_ambience)  # 추후 프롬프트 입력으로 사용

        ordered = sorted(
            candidates,
            key=lambda x: (x.final_score, x.confidence),
            reverse=True,
        )

        out: list[dict[str, Any]] = []
        for item in ordered:
            out.append(
                {
                    "place_id": item.candidate.place_id,
                    "reason": f"분위기({item.ambience_tag.value})와 이동 부담을 종합해 우선 추천합니다.",
                }
            )
        return out