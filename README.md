# FastApi-Todos — Pulse Todo

FastAPI 기반 To-Do List 애플리케이션과, 이를 둘러싼 **CI/CD · 테스트 · 정적분석 · 모니터링 · 부하테스트 · 로그 수집** DevOps 파이프라인을 구축한 프로젝트입니다. 단순 CRUD 앱(v1.0.0)에서 출발해 애니메이션 UI/UX와 풀 관측성(observability) 스택을 갖춘 v8.0.0까지 매주 누적 개선되었습니다.

---

## ✨ 주요 기능 (애플리케이션)

- **To-Do CRUD**: 할 일 추가 · 조회 · 수정 · 삭제 (`todo.json` 파일 영속화)
- **우선순위 / 마감일**: High·Medium·Low 우선순위와 마감일 기반 정렬 · 지연(overdue) 표시
- **검색 · 필터 · 정렬**: 제목/메모 검색, 전체/진행/완료 필터, 우선순위·마감일·생성순 정렬
- **진행률 대시보드**: 진행률 링(%), Total·Active·Done 통계 보드
- **부가 기능**: 완료 항목 접기, 라이트/다크 테마 전환, TXT 내보내기, 배경 인터랙션
- **관측성**: Prometheus `/metrics` 노출 및 Loki로 액세스 로그 전송

---

## 🧱 기술 스택

| 구분 | 도구 |
|---|---|
| 애플리케이션 | FastAPI, Pydantic, Uvicorn, HTML/CSS/JS |
| 컨테이너 | Docker, Docker Compose, DockerHub |
| CI/CD | Jenkins (Declarative Pipeline) |
| 테스트 | pytest, pytest-cov, pytest-html, httpx |
| 정적 분석 | SonarQube, SonarScanner (Quality Gate) |
| 메트릭 모니터링 | Prometheus, Grafana, Node Exporter, cAdvisor |
| 부하 테스트 | JMeter (+ InfluxDB) |
| 로그 수집 | Loki, python-logging-loki, LogQL |

---

## 📁 프로젝트 구조

```
FastApi-Todos/
├── docker-compose.yml          # 전체 스택(앱·모니터링·테스트) 오케스트레이션
├── fastapi-app/
│   ├── main.py                 # FastAPI 앱 · CRUD 엔드포인트 · 모니터링 미들웨어
│   ├── todo.json               # 할 일 데이터 저장 파일
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── sonar-project.properties
│   ├── templates/
│   │   └── index.html          # 단일 페이지 프런트엔드(Pulse Todo)
│   └── tests/
│       ├── test_main.py        # 단위/통합 테스트
│       └── test_integration.py
├── prometheus/
│   └── prometheus.yml          # 스크레이프 타깃(fastapi·node·cadvisor)
├── jmeter/
│   ├── fastapi_test_plan.jmx   # 부하 테스트 시나리오
│   └── Dockerfile
└── .github/workflows/deploy.yml
```

---

## 🚀 빠른 시작

### Docker Compose (전체 스택)

```bash
docker compose up -d --build
```

| 서비스 | 접속 |
|---|---|
| FastAPI 앱 | http://localhost:5001 |
| Grafana | http://localhost:3000 (admin / admin) |
| Prometheus | http://localhost:7070 |
| SonarQube | http://localhost:9000 (admin / admin) |
| Loki | http://localhost:3100 |
| Node Exporter | http://localhost:7100 |
| cAdvisor | http://localhost:8081 |

### 로컬 실행 (앱만)

```bash
cd fastapi-app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

→ 브라우저에서 `http://localhost:8000` 접속, API 문서는 `http://localhost:8000/docs` (Swagger UI).

---

## 🔌 API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/` | To-Do List 웹 페이지(HTML) |
| `GET` | `/todos` | 전체 할 일 조회 |
| `POST` | `/todos` | 할 일 추가 |
| `PUT` | `/todos/{todo_id}` | 할 일 수정 |
| `DELETE` | `/todos/{todo_id}` | 할 일 삭제 |
| `GET` | `/metrics` | Prometheus 메트릭 |

**TodoItem 모델**

```json
{
  "id": 1,
  "title": "API 응답 시간 점검",
  "description": "세부 메모(선택)",
  "completed": false,
  "due_date": "2026-06-30",
  "priority": "중"
}
```

`due_date`는 선택값(기본 `null`), `priority`는 기본값 `"중"`입니다.

---

## 🧪 테스트 & 커버리지

```bash
cd fastapi-app
pytest tests \
  --html=pytest_report/report.html --self-contained-html \
  --cov=. --cov-report=html:htmlcov
```

생성된 `pytest_report/report.html`(테스트 결과)과 `htmlcov/index.html`(커버리지)을 브라우저에서 확인할 수 있습니다.

---

## 🔁 CI/CD & 관측성 파이프라인

1. **Build & Test** — pytest 단위/통합 테스트 + 커버리지 측정
2. **Static Analysis** — SonarQube 정적분석, Quality Gate 미달 시 배포 중단
3. **Build & Push** — Docker 이미지 빌드 후 DockerHub 푸시
4. **Deploy** — 원격 서버에 컨테이너 배포 (Jenkins `sshagent`)
5. **Load Test** — JMeter 부하 테스트 후 HTML 리포트 발행
6. **Observe** — Prometheus(메트릭, Pull) · Loki(로그, Push) → Grafana 시각화

---

## 🏷️ 버전 이력

| 버전 | 핵심 내용 |
|---|---|
| v1.0.0 | To-Do 기본 앱 (FastAPI CRUD + index.html) |
| v2.0.0 | VDI/서버 배포 · GitHub · Jenkins CI/CD |
| v3.0.0 | Docker · DockerHub · 도커 파이프라인 |
| v4.0.0 | pytest · Coverage · HTML 리포트 |
| v5.0.0 | SonarQube 정적분석 · Quality Gate |
| v6.0.0 | Prometheus · Grafana · Node Exporter · cAdvisor |
| v7.0.0 | JMeter 부하/성능 테스트 |
| v8.0.0 | Loki 로그 수집 · LogQL 대시보드 |
