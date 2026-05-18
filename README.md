# Coding Assessment Platform

A full-stack, self-hosted coding assessment platform for evaluating employee technical skills. It supports algorithmic coding challenges, multiple-choice questions, framework-level tests (React, FastAPI), and SQL problems — all executed live via a self-hosted **Judge0 CE** engine.

---

## Monorepo Structure

```
coding-platform/
├── backend/          # FastAPI REST API (Python 3.11)
├── frontend/         # React 19 + Vite SPA (TypeScript)
├── aws-infra/        # AWS CDK deployment (Python, EC2-based)
└── scripts/          # Root-level utility scripts (seeding, etc.)
```

Each package has its own detailed documentation:

| Package | Docs |
|---------|------|
| Backend API | [`backend/README.md`](./backend/README.md) |
| Frontend SPA | [`frontend/README.md`](./frontend/README.md) |
| AWS Infrastructure | [`aws-infra/DOCS.md`](./aws-infra/DOCS.md) |

---

## System Overview

```
┌─────────────┐        ┌──────────────────┐        ┌──────────────┐
│   Browser   │──HTTP──▶  React Frontend  │──HTTP──▶ FastAPI Back │
│  (Candidate │        │  (Nginx :3000 /  │        │  end (:8000) │
│   / Admin)  │        │   Vite dev :5173)│        │              │
└─────────────┘        └──────────────────┘        └──────┬───────┘
                                                          │
                                      ┌───────────────────┴──────────────────┐
                                      │                                       │
                               ┌──────▼──────┐                    ┌──────────▼──────┐
                               │  PostgreSQL  │                    │   Judge0 CE     │
                               │  (port 5432)│                    │   (:2358)       │
                               └─────────────┘                    └─────────────────┘
```

### Key Roles

| Role | Description |
|------|-------------|
| **Admin** | HR / assessment managers. Log in, view dashboards, view/export candidate reports. |
| **Candidate** | Employees being assessed. Log in, attempt skill assessments, view results and badges. |

---

## Core Concepts

### Skills & Levels

Each **Skill** (e.g. Java, SQL, Python FastAPI) has 5 ordered levels that a candidate must clear sequentially:

```
Beginner → Intermediate 1 → Intermediate 2 → Specialist 1 → Specialist 2
```

Clearing a level unlocks the next one. Each level allows a **maximum of 5 attempts** (configurable via `MAX_ATTEMPTS_PER_LEVEL`).

### Assessment Flow

1. Candidate picks a skill and level on their dashboard.
2. Candidate reads instructions, then starts the session.
3. The backend picks **2 random problems** for that skill+level, creates a timed session.
4. Candidate solves both problems in the Monaco code editor.
5. On submit, the backend runs all test cases through Judge0 and scores the combined result.
6. Score ≥ 70% (configurable) → `CLEARED`, next level unlocked, badge awarded.
7. Admin can view results and download PDF / CSV reports.

### Question Types

| Type | How it's evaluated |
|------|-------------------|
| `coding` | Code submitted to Judge0; stdin/stdout compared against test cases |
| `mcq` | Option index matched against `correct_option_index` |
| `framework` | Multi-file ZIP submitted to Judge0 (language_id 89); runs pytest or Jest |
| `sql` | SQLite query submitted to Judge0 (language_id 82); output compared per test case |

### Anti-Cheat (Proctoring)

The frontend records and POSTs **violation events** to the backend during an active session:

- Tab switch / window blur / visibility hidden
- Fullscreen exit
- Paste / copy / cut / select-all attempts
- DevTools keyboard shortcuts
- Right-click context menu

All violations are stored in `session_violations` and visible to admins in candidate reports.

---

## Quick Start (Local Development)

### Prerequisites

- **Python 3.11+** and **pip**
- **Node.js 20+** and **npm**
- **PostgreSQL 13+** running locally
- A reachable **Judge0 CE** instance (use the public `https://ce.judge0.com` for development)

### 1 — Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL and JUDGE0_BASE_URL at minimum

# Run database migrations
alembic upgrade head

# Start the dev server
uvicorn app.main:app --reload --port 9515
```

API docs available at: **http://localhost:9515/docs**

### 2 — Frontend

```bash
cd frontend

npm install

# Copy and configure environment
cp .env.example .env
# Set VITE_API_URL=http://localhost:9515

npm run dev
```

App available at: **http://localhost:9514**

---

## Environment Variables — Quick Reference

### Backend (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | Full SQLAlchemy DB URL |
| `JUDGE0_BASE_URL` | ✅ | `https://ce.judge0.com` | Judge0 CE endpoint |
| `JWT_SECRET_KEY` | ✅ | insecure dev default | Secret for signing JWTs |
| `ENV` | — | `development` | Set to `production` to enforce CORS |
| `CORS_ALLOWED_ORIGINS` | Prod only | — | Comma-separated allowed origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | — | `15` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | — | `7` | Refresh token TTL |
| `SCORE_PASS_THRESHOLD` | — | `70` | Minimum % score to clear a level |
| `MAX_ATTEMPTS_PER_LEVEL` | — | `5` | Max attempts per skill+level |
| `DB_SECRET_ARN` | — | — | AWS Secrets Manager ARN (alternative to inline creds) |

### Frontend (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ✅ | Backend API base URL |

---

## Deployment

The platform supports two deployment models:

### Option A — Local / On-Premise VM (Docker Compose)

Run the full stack on any VM with Docker and Nginx installed.

```bash
cp .env.example .env          # fill in POSTGRES_PASSWORD, JWT_SECRET_KEY, JUDGE0_BASE_URL
docker compose up -d --build
docker compose exec backend python /scripts/seed.py     # first run only (creates tables, stamps alembic, seeds data)
```
Configure the host VM's Nginx to route traffic to the containers using the provided [`nginx.conf`](./nginx.conf):

```bash
sudo cp nginx.conf /etc/nginx/sites-available/coding-platform
sudo ln -s /etc/nginx/sites-available/coding-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

See [`.env.example`](./.env.example) for all configurable settings.

### Option B — AWS (CDK + EC2)

Automated single-instance deployment via AWS CDK. See [`aws-infra/DOCS.md`](./aws-infra/DOCS.md) for the full guide.


## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4, shadcn/ui, Monaco Editor, Zustand, TanStack Query |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, python-jose, bcrypt |
| Database | PostgreSQL 13+ |
| Code Execution | Judge0 CE (self-hosted via Docker) |
| Infrastructure | AWS CDK (Python), EC2, Docker Compose, Nginx |
