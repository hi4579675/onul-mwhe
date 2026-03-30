# Changelog

- `Unreleased` 섹션에 먼저 기록 후 릴리즈 시 버전 섹션으로 이동
- 메시지는 "왜 변경했는지" 중심으로 1줄 요약
- 테스트/문서 변경도 기능 변경과 분리하여 기록

형식:
- 날짜: YYYY-MM-DD
- 버전: SemVer 권장 (예: v1.0.1)
- 유형: Added / Changed / Fixed / Removed

---

## [Unreleased]

### Added
- Retrieve 단계에 Redis cache-aside를 도입하여 후보 조회 성능을 개선했다.
- Feasibility 단계에 영업시간 판정(`open/closed/unknown`) 로직을 추가했다.
- Score 단계에 evidence 기반 `ambience_tag` 추정 및 `confidence` 계산을 추가했다.

- feasibility business-hours 파싱 단위 테스트 추가
- retrieve cache hit/miss 단위 테스트 추가
- score confidence 분리 검증 테스트 추가

- route-service에 `generate` 응답 저장(`routes` 테이블) 및 `GET /api/v1/routes/history` 최소 조회 API를 추가했다.
- Flyway 기반 초기 스키마(`V1__create_routes_table.sql`)를 도입해 `ddl-auto: validate` 환경에서도 저장/조회 경로를 안정화했다.



### Changed
- Route 조합 로직을 슬롯 중복 제거 방식으로 변경해 슬롯당 최대 1개 추천되도록 했다.
- fallback 조건을 retrieve/feasibility/score 결과 기반으로 명확화했다.

- route 조합 로직을 전역 점수 우선 방식에서 슬롯 순서 기반 방식으로 변경해, 요청 `timeslots` 순서를 항상 보장하도록 정렬 규칙을 고정함.
- 동일 `place_id` 중복 선택을 차단해 한 응답 내 장소 중복 추천을 방지함.
- 슬롯 선택 실패를 `dropped_slots` 내부 로그로 표준화해 운영 시 원인 추적성을 강화함.

- Kakao 외부 호출에 retry(최대 2회, 지수 백오프)와 circuit breaker를 적용해 장애 전파를 완화함.
- Kakao 호출 실패 로그를 timeout/network/http_4xx/http_5xx/circuit_open 분류 필드로 표준화함.
- 외부 API 복원력 설정값(retry/cb/timeout)을 환경설정으로 분리해 운영 튜닝 가능성을 높임.

- route generate/history 경로에서 `X-Correlation-ID`를 응답 헤더와 서비스 로그에 일관 전파하도록 정리했다.
- Phase 1 사용자 식별은 JWT 대신 `X-User-Id` 헤더 기반으로 임시 운영하도록 명시했다.

### Fixed
- 테스트 실행 경로/모듈 import 이슈를 정리하고 회귀 테스트를 보강했다.
- `score_service`에서 confidence 계산값이 응답에 반영되지 않던 문제 수정
- `feasibility_service` 중복 함수 정의 및 불필요 import 정리

### Removed
- 

---

## [v1.0.1] - 2026-03-27

### Added
- `route generate` API 계약 문서 초안 작성 (`docs/route-generate-contract.md`)
- ai-service 기본 라우터(`/health`, `/api/v1/route/generate`) 연결
- Retrieve/Feasibility/Score 서비스 스켈레톤 추가
- API/서비스 단위 테스트 추가 (`test_route`, `test_retrieve_service`, `test_score_service`)

### Changed
- 응답 스키마 정합성 검증 강화 (`unknown_count`, `order`, `slot`)

### Fixed
- 모듈 경로/실행 경로 관련 테스트 import 이슈 정리

### Removed
- 