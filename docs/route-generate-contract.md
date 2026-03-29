# 📍 API Contract: Route Generation

- **File Path**: `docs/route-generate-contract.md`
- **Version**: v1.0.1
- **Last Updated**: 2026-03-27
- **Status**: Fixed

## 0. Revision History
| Version | Date | Author | Change Type | Summary |
| :--- | :--- | :--- | :--- | :--- |
| v1.0.1 | 2026-03-27 | Team | Changed | request/response 필드 및 에러 코드 고정 |
| v1.0.0 | 2026-03-27 | Team | Added | 초기 계약서 작성 |
---

## 1. 개요
사용자의 취향/지역 정보를 바탕으로 하루 동선을 생성하는 `ai-service`(FastAPI) 핵심 API.
`route-service`(Spring Boot)에서 내부 호출한다.

- **Method**: `POST`
- **Path**: `/api/v1/route/generate`
- **Content-Type**: `application/json`
- **Caller**: `route-service` only (internal)

---

## 2. Request

### 2.1 Header
| Header Name | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `X-Correlation-ID` | Yes | 분산 추적용 UUID v4 | `550e8400-e29b-41d4-a716-446655440000` |
| `Content-Type` | Yes | 데이터 타입 | `application/json` |

### 2.2 Body
| Field Name | Type | Required | Constraints | Description | Example |
| :--- | :---: | :---: | :--- | :--- | :--- |
| `region` | String | Yes | 1~30자 | 중심 지역명 | `"성수"` |
| `timeslots` | Array[String] | Yes | 최소 2개, 중복 불가, enum 제한 | 방문 슬롯 목록 | `["lunch","cafe","dinner"]` |
| `preferred_ambience` | Array[String] | Yes | 1~4개, enum 제한 | 선호 분위기 | `["cozy","quiet"]` |
| `food_type` | Array[String] | No | 0~5개 | 선호 음식 카테고리 | `["한식","일식"]` |
| `budget_level` | String | Yes | `low \| normal \| high` | 예산 수준 | `"normal"` |

> `user_id`는 Request Body에서 받지 않는다.  
> 사용자 식별은 `route-service`가 JWT에서 추출하여 내부 컨텍스트로만 사용한다.

### 2.3 Enum 정의

#### `timeslots`
- `breakfast`, `lunch`, `cafe`, `activity`, `dinner`, `dessert`

#### `preferred_ambience`
- `quiet`, `lively`, `cozy`, `work_friendly`

---

## 3. Response

### 3.1 Success (200 OK)
| Field Name | Type | Description |
| :--- | :---: | :--- |
| `plan` | Array[PlanItem] | `order` 오름차순 동선 |
| `fallback_used` | Boolean | 폴백 템플릿 사용 여부 |
| `unknown_count` | Integer | `confidence < 0.4` 포함 개수 |
| `correlation_id` | String | 요청의 `X-Correlation-ID` 그대로 반환 |

#### PlanItem
| Field Name | Type | Description |
| :--- | :---: | :--- |
| `place_id` | String | 카카오 장소 ID (`kakao_...`) |
| `slot` | String | 시간대 슬롯 |
| `order` | Integer | 동선 순서 (1부터) |
| `reason` | String | 추천 이유 (한글) |
| `confidence` | Float | 0.0 ~ 1.0 |
| `ambience_tag` | String | `quiet/lively/cozy/work_friendly/unknown` |

### 3.2 Error (4xx/5xx)
| Field Name | Type | Description |
| :--- | :---: | :--- |
| `code` | String | 표준 에러 코드 |
| `message` | String | 에러 상세 |
| `fallback_used` | Boolean | 폴백 데이터 제공 여부 |
| `correlation_id` | String | 추적 ID |

#### Error Code 표준
- `VALIDATION_ERROR`
- `KAKAO_API_ERROR`
- `LLM_TIMEOUT`
- `UPSTREAM_UNAVAILABLE`
- `INTERNAL_ERROR`

---

## 4. JSON Samples

### 4.1 Request Example

```json
{
  "region": "성수",
  "timeslots": ["lunch", "cafe", "activity", "dinner"],
  "preferred_ambience": ["cozy", "quiet"],
  "food_type": ["양식"],
  "budget_level": "normal"
}
```
### 4.2 Success Example (200)
```json
{
  "plan": [
    {
      "place_id": "kakao_12345",
      "slot": "lunch",
      "order": 1,
      "reason": "조용하고 감성적인 분위기로 점심 시작에 적합합니다.",
      "confidence": 0.74,
      "ambience_tag": "cozy"
    },
    {
      "place_id": "kakao_22345",
      "slot": "cafe",
      "order": 2,
      "reason": "이동 거리가 짧고 조용한 좌석 비중이 높습니다.",
      "confidence": 0.71,
      "ambience_tag": "quiet"
    }
  ],
  "fallback_used": false,
  "unknown_count": 0,
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 4.3 Error Example (503)
```json
{
  "code": "UPSTREAM_UNAVAILABLE",
  "message": "Kakao API timeout",
  "fallback_used": true,
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---
## 5. Validation Rules (서버 동작 기준)
- `timeslots`는 중복 불가, 최소 2개
- `preferred_ambience`는 최소 1개, 최대 4개
- `budget_level`은 `low/normal/high`만 허용
- `X-Correlation-ID` 누락 시 `422` 반환
- JSON body 누락/형식 오류 시 `422` 반환
---
## 6. Fallback Semantics
- `fallback_used=true` 조건:
  - 외부 API 타임아웃
  - 상위 의존 서비스 일시 장애
  - 내부 추천 파이프라인에서 후보가 0개
- fallback 응답이어도 계약 스키마는 동일하게 유지한다.
- fallback 응답 시 `plan`은 빈 배열일 수 있다.
---
## 7. Non-Goals (현재 버전에서 하지 않는 것)
- LLM이 후보 외 장소를 생성하는 기능
- 실시간 교통/혼잡도 기반 동선 최적화
- 개인화 모델 학습 결과의 온라인 반영

## 8. Runtime Selection Rules (구현 동작 규약)

- `plan`은 요청 `timeslots` 기준으로 슬롯당 최대 1개만 포함한다.
- 같은 `place_id`는 한 응답 내에서 중복 추천하지 않는다.
- `plan` 길이는 요청 `timeslots` 길이 이하일 수 있다(필터/점수 결과에 따라 축소 가능).
- `fallback_used=true`는 아래 경우 발생할 수 있다:
  - Retrieve 결과가 비어 있음
  - Feasibility 적용 후 후보가 0개
  - Score 적용 후 선택 가능한 후보가 0개
  - 외부 의존성 오류/타임아웃