# Architecture Decisions

핵심 의사결정을 ADR 형태로 기록합니다.
(길게 쓰지 말고 Why 중심으로 짧게)

---

## ADR Template

## ADR-XXX: [제목]

- **Date**: YYYY-MM-DD
- **Status**: Proposed / Accepted / Superseded
- **Context**
  - 
- **Decision**
  - 
- **Alternatives Considered**
  - Option A:
  - Option B:
- **Consequences**
  - 장점:
  - 단점:
- **Follow-up**
  - [ ] 문서 업데이트
  - [ ] 테스트 추가
  - [ ] 모니터링 지표 반영
---


## ADR-001: AI 엔진을 FastAPI로 분리

- **Date**: 2026-03-27
- **Status**: Accepted
- **Context**
  - Kakao API 비동기 병렬 호출 필요
  - LLM/프롬프트 교체 주기가 빠름
- **Decision**
  - `ai-service`를 Python(FastAPI)로 분리
- **Consequences**
  - 장점: AI 실험 속도 향상, async 처리 유리
  - 단점: 서비스 간 연동/관측/장애 대응 복잡도 증가

---

## ADR-002: LLM 역할 제한 (편집기 전략)

- **Date**: 2026-03-27
- **Status**: Accepted
- **Context**
  - 환각 및 비용 통제가 필요
- **Decision**
  - LLM은 후보 생성 금지, re-rank/설명만 수행
- **Consequences**
  - 장점: 일관성/비용/재현성 향상
  - 단점: 초기 추천 다양성 제한 가능

---

## ADR-003: Feasibility First

- **Date**: 2026-03-27
- **Status**: Accepted
- **Context**
  - “좋은 장소”보다 “갈 수 있는 동선”이 우선
- **Decision**
  - 이동/영업/체류 규칙을 선필터로 적용
- **Consequences**
  - 장점: 사용자 불만(비현실 추천) 감소
  - 단점: 후보 수 감소로 fallback 빈도 증가 가능

---

## ADR-004: route generate 계약 우선 개발

- **Date**: 2026-03-27
- **Status**: Accepted
- **Context**
  - 서비스 간 개발 병렬화 필요
- **Decision**
  - `docs/route-generate-contract.md`를 기준으로 구현/테스트 진행
- **Consequences**
  - 장점: 프론트/백엔드/AI 병렬 개발 가능
  - 단점: 계약 변경 시 하위 서비스 동시 수정 필요

## ADR-005: Retrieve에 Redis Cache-Aside 도입

- **Date**: 2026-03-27
- **Status**: Accepted
- **Context**
  - Kakao API 호출 빈도가 높아질수록 응답 지연/쿼터 소모가 증가함
- **Decision**
  - `place:candidates:v1:{region}:{slot}` 키로 후보 조회 결과를 TTL 캐시한다
- **Consequences**
  - 장점: 응답시간 단축, 외부 API 호출량 감소
  - 단점: TTL 구간 내 데이터 최신성 지연 가능

---

## ADR-006: Confidence를 Score와 분리 계산

- **Date**: 2026-03-27
- **Status**: Accepted
- **Context**
  - 점수(final_score)와 설명 신뢰도(confidence)를 같은 값으로 두면 해석력이 떨어짐
- **Decision**
  - confidence는 evidence 개수/질 기반으로 별도 계산한다
- **Consequences**
  - 장점: 추천 이유의 신뢰도를 독립적으로 표현 가능
  - 단점: 계산 규칙 복잡도 증가, 튜닝 포인트 추가