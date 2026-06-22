# InsightFlow AI — Smart Career Analytics & Data Science Platform

An enterprise-grade, full-stack SaaS platform combining **AI career analytics** (resume
analysis, salary prediction, career recommendations) with a **dataset analytics / AutoML
suite** (Auto EDA, AutoML, RAG-powered chat assistant, natural-language-to-pandas queries).

Built with **FastAPI + React 19 + TypeScript + PostgreSQL**, ML via **scikit-learn / XGBoost
/ Prophet**, and AI via **Gemini / OpenAI + LangChain + ChromaDB (RAG)**.

---

## ✨ Features

| Module | Description |
|---|---|
| 🔐 Auth | Register, login, email verification, forgot/reset password, JWT, protected routes |
| 📄 Resume Analyzer | PDF parsing, skill/education extraction, AI-generated ATS score, skill-gap analysis, roadmap, downloadable PDF report |
| 💰 Salary Prediction | XGBoost regression model trained on a synthetic market-rate dataset; returns range + demand + growth |
| 🧭 Career Recommendations | Matches skills against a role catalogue (Data Scientist, ML Engineer, AI Engineer, etc.) with learning paths |
| 📊 Dataset Analytics (Auto EDA) | Upload CSV/Excel → missing values, outliers (IQR), stats, correlation matrix, histograms, boxplots |
| 🤖 AI Dataset Chat (RAG) | ChromaDB + LangChain-style retrieval over your dataset's EDA report; ask questions in plain English |
| 🗣️ NL → Pandas | Translates natural-language questions into executed pandas expressions |
| ⚙️ AutoML | Trains & compares Logistic Regression / Random Forest / XGBoost (classification & regression), plus Prophet for time series |
| 🧠 AI Insight Generator | Narrative business insights generated from the EDA report |
| 📈 Dashboard | KPIs, charts, model comparisons — built with Recharts |
| 📑 Report Generator | PDF (ReportLab), CSV, and Excel exports |
| 🛡️ Admin Dashboard | User management, dataset/usage stats, activity logs, API usage analytics |

---

## 🏗️ Architecture

```
insightflow-ai/
├── backend/                  FastAPI application
│   ├── app/
│   │   ├── api/v1/endpoints/ # auth, resume, career, datasets, nl_query, automl, chat, reports, admin
│   │   ├── core/             config, security (JWT/bcrypt), deps, middleware
│   │   ├── database/         SQLAlchemy session/engine
│   │   ├── models/           SQLAlchemy ORM models
│   │   ├── schemas/          Pydantic request/response schemas
│   │   ├── services/         AI provider abstraction, resume/career/report/RAG services
│   │   ├── ml/                salary model, EDA engine, AutoML engine
│   │   ├── utils/             email utilities
│   │   ├── celery_app.py     background task definitions
│   │   └── main.py           FastAPI entrypoint
│   ├── alembic/               DB migrations
│   ├── scripts/seed_admin.py  creates an initial admin account
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 React 19 + TypeScript + Tailwind + shadcn-style UI
│   ├── src/
│   │   ├── pages/             Landing, Auth, Dashboard, Resume, Salary, Career, Datasets, Chat, AutoML, Admin
│   │   ├── components/layout/ Sidebar, DashboardLayout, ProtectedRoute
│   │   ├── api/client.ts      Axios instance with JWT refresh interceptor
│   │   └── store/authStore.ts Zustand auth store
│   └── Dockerfile
├── nginx/nginx.conf          Reverse proxy (routes /api → backend, / → frontend)
└── docker-compose.yml        Postgres, Redis, FastAPI, Celery worker, React, Nginx
```

---

## 🚀 Quick Start (Docker — recommended)

```bash
git clone <your-repo-url> insightflow-ai
cd insightflow-ai

cp backend/.env.example backend/.env
# edit backend/.env and add your OPENAI_API_KEY and/or GEMINI_API_KEY

docker compose up --build
```

- Frontend: http://localhost:5173 (or http://localhost via the nginx reverse proxy)
- Backend API docs (Swagger): http://localhost:8000/api/docs
- Backend API docs (ReDoc): http://localhost:8000/api/redoc

Create an admin user:
```bash
docker compose exec backend python -m scripts.seed_admin
# creates admin@insightflow.ai / ChangeMe123! — change this immediately
```

---

## 🧑‍💻 Local Development (without Docker)

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Make sure Postgres & Redis are running locally and DATABASE_URL/REDIS_URL match
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "init"
alembic upgrade head
```
(Note: `app.main` also calls `Base.metadata.create_all()` on startup for convenience in
development — use Alembic exclusively in production.)

---

## 🔑 Environment Variables (backend/.env)

See `backend/.env.example` for the full list. Key ones:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | JWT signing secret — **change in production** |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` / `CELERY_*` | Redis & Celery broker/backend |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` | AI provider keys (resume analysis, insights, RAG chat, NL→pandas) |
| `DEFAULT_AI_PROVIDER` | `gemini` or `openai` |
| `SMTP_*` | Outbound email for verification/reset links (falls back to console logging in dev) |

All AI-powered endpoints (`ai_complete_json` / `ai_complete`) **fail gracefully** with
deterministic fallbacks if no API key is configured, so the platform remains demoable
without live credentials.

---

## 📚 Key API Endpoints

All under `/api/v1`. Full interactive docs at `/api/docs`.

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/forgot-password
POST   /auth/reset-password
POST   /auth/verify-email
GET    /auth/me
PUT    /auth/me

POST   /resume/analyze
GET    /resume/history
GET    /resume/{id}

POST   /salary/predict
GET    /salary/history
POST   /career/recommend

POST   /datasets/upload
GET    /datasets
GET    /datasets/{id}
GET    /datasets/{id}/eda
DELETE /datasets/{id}

POST   /nl-query
POST   /automl/run
GET    /automl/runs/{dataset_id}

POST   /chat/message
GET    /chat/sessions/{id}/history

GET    /reports/resume/{id}/pdf
GET    /reports/dataset/{id}/pdf
GET    /reports/dataset/{id}/csv

GET    /admin/overview
GET    /admin/users
PATCH  /admin/users/{id}/toggle-active
GET    /admin/activity-logs
GET    /admin/api-usage
```

---

## 🛡️ Security

- JWT access + refresh tokens, bcrypt password hashing
- Rate limiting via `slowapi`
- Pydantic input validation on every endpoint
- CORS allow-list via `CORS_ORIGINS`
- SQL injection prevention via SQLAlchemy ORM (no raw string interpolation)
- NL→Pandas queries execute in a restricted `eval()` namespace (no builtins beyond a safe allow-list)

---

## 🗺️ Roadmap / Things to Harden for Real Production Use

- Replace the synthetic salary-prediction training data with a real labeled dataset
- Move long-running EDA/AutoML jobs to Celery (`run_eda_async` task is scaffolded) with
  a polling or WebSocket status endpoint instead of running them inline in the request
- Add per-user/file storage quotas and S3-compatible object storage instead of local disk
- Add Stripe billing for the "Revenue Analytics" admin panel
- Add comprehensive test suite (pytest + React Testing Library) and CI pipeline
- Swap `create_all()` for Alembic-only schema management in production

---

## 📄 License

MIT — built as a portfolio-grade reference implementation.
