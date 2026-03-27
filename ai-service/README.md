# ai-service

FastAPI 기반 동선 추천 엔진.

## 포함 기능(스켈레톤)

- Retrieve (후보 수집)
- Feasibility Filter (실현 가능성 필터)
- Score (비-LLM 점수화)
- Re-rank (LLM 재정렬 자리)

## 실행

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```
