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



### Changed
- Route 조합 로직을 슬롯 중복 제거 방식으로 변경해 슬롯당 최대 1개 추천되도록 했다.
- fallback 조건을 retrieve/feasibility/score 결과 기반으로 명확화했다.

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