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
- 

### Changed
- 

### Fixed
- 

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