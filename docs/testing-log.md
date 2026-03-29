# Testing Log

테스트 실행 결과를 날짜별로 누적 기록합니다.
(수동/Postman + 자동/pytest 모두 기록)

---
---

## 테스트 분류 기준

- Contract Test: 요청/응답 스키마, 상태코드 검증
- Integration Test: 서비스 간 호출 및 헤더 전파 검증
- Resilience Test: timeout/retry/fallback 동작 검증
- Regression Test: 과거 이슈 재발 방지 검증

## 실패 기록 규칙

실패 케이스는 아래 포맷으로 반드시 기록:
- Symptom:
- Root Cause:
- Fix:
- Preventive Test:


## Template

### YYYY-MM-DD HH:mm (KST)

- **환경**
  - Branch: ``
  - Commit: ``
  - Service: `ai-service` / `route-service`
  - Command: ``

- **테스트 항목**
  - [ ] 정상 요청 200
  - [ ] 헤더 누락 422
  - [ ] body validation 422
  - [ ] fallback 동작 확인
  - [ ] correlation_id 전파 확인

- **결과**
  - Passed:
    - 
  - Failed:
    - 

- **비고**
  - 

---

## 2026-03-27 (회고 기록)

- 초기 이슈
  - 401 Unauthorized: Security 인증 정책으로 route endpoint 차단
  - 404 Not Found: 포트/컴포넌트 스캔 이슈
  - 422 Validation: `X-Correlation-ID`/Body 누락

- 조치
  - route endpoint 경로/호출 포트 정리
  - ai-service 계약 기반 request/response 검증 정착
  - route-service 경유 호출 + fallback 동작 확인
  - unit/contract 테스트 추가

- 결과
  - ai-service 직접 호출 정상(200)
  - route-service 경유 시 계약 응답 확인
  - pytest 통과 (`route/retrieve/score`)
  
## 2026-03-27

- **환경**
  - Service: `ai-service`
  - Command: `pytest -q`

- **결과**
  - `4 passed in 0.48s` (route API 테스트)
  - retrieve/score 단위 테스트 추가 완료

- **수동 검증**
  - `POST /api/v1/route/generate` with `X-Correlation-ID` + JSON body -> 200
  - 헤더/바디 누락 시 422 확인

- **비고**
  - 초기 401/404/422 원인 분리 진단 완료 (보안/포트/요청형식)

## 2026-03-27 (고도화 반영)

- **환경**
  - Service: `ai-service`
  - Command: `pytest -q`

- **테스트 항목**
  - [x] Contract Test: route API 정상/검증 실패 케이스
  - [x] Unit Test: retrieve 서비스
  - [x] Unit Test: score 서비스
  - [x] fallback 동작 확인

- **결과**
  - Passed:
    - route API 테스트 통과
    - retrieve/score 단위 테스트 통과
  - Failed:
    - 없음

- **수동 검증**
  - `POST /api/v1/route/generate` with `X-Correlation-ID` + JSON body -> 200
  - 헤더/바디 누락 -> 422
  - 후보 없음/예외 시 `fallback_used=true` 확인

- **비고**
  - 슬롯 중복 제거 로직 반영 후 `plan` 구성이 요청 슬롯 수 이하로 유지됨