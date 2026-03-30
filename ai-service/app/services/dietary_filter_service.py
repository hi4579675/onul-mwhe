from __future__ import annotations

from app.models.schemas import AllergyType
from app.services.feasibility_service import FeasibleCandidate


class DietaryFilterService:
    """
    MVP 규칙 기반 식이 필터.
    카테고리/키워드/장소명 문자열에 알레르겐·비건 비적합 신호가 있으면 제외한다.
    """

    _ALLERGY_TOKENS: dict[AllergyType, set[str]] = {
        AllergyType.PEANUT: {"땅콩", "피넛", "peanut"},
        AllergyType.SHELLFISH: {"갑각류", "새우", "게", "랍스터", "조개", "굴", "shellfish", "shrimp", "crab"},
        AllergyType.DAIRY: {"우유", "치즈", "버터", "크림", "요거트", "유제품", "milk", "cheese", "cream", "yogurt"},
        AllergyType.NONE: set(),
    }

    # vegan=true일 때 제외할 힌트(보수적으로 운영)
    _NON_VEGAN_TOKENS: set[str] = {
        "고기",
        "소고기",
        "돼지",
        "돼지고기",
        "삼겹살",
        "치킨",
        "닭",
        "생선",
        "회",
        "해산물",
        "육회",
        "곱창",
        "족발",
        "치즈",
        "버터",
        "크림",
        "우유",
        "요거트",
        "beef",
        "pork",
        "chicken",
        "fish",
        "seafood",
        "cheese",
        "milk",
        "butter",
        "cream",
    }

    def apply(
        self,
        candidates: list[FeasibleCandidate],
        allergies: list[AllergyType],
        vegan: bool,
    ) -> list[FeasibleCandidate]:
        if not candidates:
            return []

        if not allergies and not vegan:
            return candidates

        filtered: list[FeasibleCandidate] = []
        allergy_set = set(allergies)
        for candidate in candidates:
            haystack = self._to_haystack(candidate)
            if self._has_allergy_conflict(haystack, allergy_set):
                continue
            if vegan and self._has_non_vegan_signal(haystack):
                continue
            filtered.append(candidate)
        return filtered

    def _has_allergy_conflict(self, haystack: str, allergies: set[AllergyType]) -> bool:
        if not allergies or AllergyType.NONE in allergies:
            return False
        for allergy in allergies:
            tokens = self._ALLERGY_TOKENS.get(allergy, set())
            if any(token in haystack for token in tokens):
                return True
        return False

    def _has_non_vegan_signal(self, haystack: str) -> bool:
        return any(token in haystack for token in self._NON_VEGAN_TOKENS)

    @staticmethod
    def _to_haystack(candidate: FeasibleCandidate) -> str:
        parts: list[str] = [candidate.name, candidate.category_name]
        if candidate.keywords:
            parts.extend(candidate.keywords)
        return " ".join(part.lower() for part in parts if part)
