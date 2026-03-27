# ai-service/app/models/schemas.py
from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------- Enums ----------
class TimeSlot(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    cafe = "cafe"
    activity = "activity"
    dinner = "dinner"
    dessert = "dessert"


class Ambience(str, Enum):
    quiet = "quiet"
    lively = "lively"
    cozy = "cozy"
    work_friendly = "work_friendly"


class BudgetLevel(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"


class AmbienceTag(str, Enum):
    quiet = "quiet"
    lively = "lively"
    cozy = "cozy"
    work_friendly = "work_friendly"
    unknown = "unknown"


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    KAKAO_API_ERROR = "KAKAO_API_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    UPSTREAM_UNAVAILABLE = "UPSTREAM_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# ---------- Request ----------
# 사용자가 우리에게 보내는 데이터의 형식을 정의한다.
class RouteGenerateRequest(BaseModel):
    # extra="forbid": "계약서에 없는 데이터는 아예 받지도 않겠다"
    model_config = ConfigDict(extra="forbid")

    # 자바의 @Size(min=1, max=30) 와 같다고 보면 됨 
    region: Annotated[str, Field(min_length=1, max_length=30)]
    timeslots: Annotated[list[TimeSlot], Field(min_length=2)]
    preferred_ambience: Annotated[list[Ambience], Field(min_length=1, max_length=4)]
    food_type: Annotated[list[str], Field(default_factory=list, max_length=5)]
    budget_level: BudgetLevel

    # field_validator: "데이터가 들어온 직후" 실행되는 자동 검사기
    @field_validator("timeslots")
    @classmethod
    def validate_timeslots_unique(cls, v: list[TimeSlot]) -> list[TimeSlot]:
    # 중복된 시간대가 있는지 체크 (예: 점심, 점심 이렇게 보내면 에러!)
        if len(set(v)) != len(v):
            raise ValueError("timeslots must not contain duplicates")
        return v

    @field_validator("food_type")
    @classmethod
    def validate_food_type_non_blank(cls, v: list[str]) -> list[str]:
        for item in v:
            if not item or not item.strip():
                raise ValueError("food_type must not contain blank values")
        return v


# ---------- Success Response ----------
# AI가 내뱉는 결과물 검수 환각 방지 
class PlanItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    place_id: str = Field(pattern=r"^kakao_[A-Za-z0-9_-]+$")
    slot: TimeSlot
    order: Annotated[int, Field(ge=1)]
    reason: Annotated[str, Field(min_length=1, max_length=300)]
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    ambience_tag: AmbienceTag


class RouteGenerateSuccessResponse(BaseModel):
  # model_validator: 모든 데이터가 채워진 후 "전체적인 정합성"을 봄
    model_config = ConfigDict(extra="forbid")

    plan: list[PlanItem]
    fallback_used: bool
    unknown_count: Annotated[int, Field(ge=0)]
    correlation_id: str

    @model_validator(mode="after")
    def validate_plan(self) -> "RouteGenerateSuccessResponse":
        # order 중복/누락 방지 (1..N)
        orders = [item.order for item in self.plan]
        if orders and sorted(orders) != list(range(1, len(self.plan) + 1)):
            raise ValueError("plan.order must be contiguous starting from 1")

        # slot 중복 방지
        # 예 : 점심 두번 먹으라고 추천하면 안됨 
        slots = [item.slot for item in self.plan]
        if len(set(slots)) != len(slots):
            raise ValueError("plan.slot must not contain duplicates")

        # unknown_count 정합성
        # 예 : 모르면 모른다고 하기
        actual_unknown = sum(1 for item in self.plan if item.ambience_tag == AmbienceTag.unknown)
        if self.unknown_count != actual_unknown:
            raise ValueError("unknown_count does not match plan.ambience_tag=unknown count")

        return self


# ---------- Error Response ----------
class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    reason: str


class RouteGenerateErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ErrorCode
    message: str
    fallback_used: bool
    correlation_id: str
    details: list[ErrorDetail] = Field(default_factory=list)