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

