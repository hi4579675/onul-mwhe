# 오늘뭐해 🗺️

> 오늘 어디 갈지 모르겠을 때 — AI가 하루 동선을 짜드립니다

지역 하나 입력하면 점심 · 카페 · 액티비티 · 저녁까지  
취향에 맞는 하루 코스를 추천해주는 개인화 서비스

---

## 서비스 소개

**"성수 가고 싶은데 뭐 할지 모르겠어"**

그 한 마디면 됩니다.  
온보딩에서 취향을 간단히 설정하면, AI가 실현 가능한 하루 동선을 만들어드립니다.

---

## 기술 스택

| 영역 | 기술 |
|---|---|
| AI 엔진 | FastAPI · Claude API · Kakao Local API |
| 백엔드 | Spring Boot 3 · PostgreSQL · Redis |
| 앱 | React Native (Expo) |
| 인프라 | Docker Compose · Railway |

---

## 아키텍처

```
[앱] → [API Gateway] → [route-service] → [ai-service]
                     ↘ [user-service]
```

**ai-service** (FastAPI) — Kakao API 수집 → Feasibility 검증 → Score 계산 → Claude 재랭킹  
**route-service** (Spring Boot) — 동선 저장 · 히스토리 · 통계  
**user-service** (Spring Boot) — 카카오 로그인 · 취향 프로필

---

## 로컬 실행

```bash
git clone https://github.com/{username}/onul-mwhe.git
cd 오늘뭐해

cp .env.example .env
# .env에 KAKAO_API_KEY, ANTHROPIC_API_KEY 입력

docker-compose up
```

---

## 구현 현황

- [x] ai-service 파이프라인 (Retrieve → Feasibility → Score → Re-rank)
- [ ] route-service (동선 저장/히스토리)
- [ ] user-service (카카오 로그인)
- [ ] React Native 앱

---
