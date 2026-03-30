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


  ## 2026-03-27 (stabilization)

- **환경**
  - Service: `ai-service`
  - Command: `pytest -q`

- **결과**
  - score/retrieve/route + feasibility 테스트 통과
  - confidence/캐시/영업시간 회귀 테스트 추가

- **비고**
  - score와 confidence 분리 반영 후 계약 응답 일관성 확인

  ## 2026-03-29 (외부 API 복원력 적용)

- **환경**
  - Service: `ai-service`
  - Command: `pytest -q`

- **테스트 항목**
  - [x] Kakao timeout 발생 시 retry 2회 동작
  - [x] 연속 실패 시 circuit breaker open 동작
  - [x] 후보 수집 실패 시 상위 fallback 경로(`fallback_used=true`) 확인

- **결과**
  - Passed:
    - retry/circuit breaker 단위 테스트 통과
    - route fallback 경로 검증 통과
  - Failed:
    - 없음

- **비고**
  - 장애 유형 로그 분류 필드(timeout/network/http_4xx/http_5xx/circuit_open) 적용


## 2026-03-30 (route-service 저장/조회 E2E)

- **환경**
  - Service: `backend (app-module + route-module)`, `ai-service`
  - Runtime: `docker-compose.e2e.yml`
  - DB: PostgreSQL (Flyway 적용)
  - Command:
    - `docker compose -f docker-compose.e2e.yml up -d --build`
    - Postman/PowerShell로 API 호출 검증

- **테스트 항목**
  - [x] `POST /api/v1/routes/generate` 응답 200
  - [x] generate 응답 DB 저장 (`routes`) 확인
  - [x] `GET /api/v1/routes/history` 조회 정상
  - [x] `X-Correlation-ID` 전파(응답/로그) 확인

- **결과**
  - Passed:
    - generate -> save -> history 시나리오 정상 동작
    - 사용자(`X-User-Id`) 기준 이력 조회 정상
  - Failed:
    - 없음

- **비고**
  - 초기에는 ai-service 환경변수(`KAKAO_REST_API_KEY`) 미주입으로 기동 실패가 있었고, compose env 주입 후 정상화함.
  - 콘솔(cmd)에서 `Invoke-RestMethod` 실행 이슈가 있어 PowerShell/Postman 기반으로 검증함.