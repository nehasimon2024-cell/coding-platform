# Backend — Developer Documentation

FastAPI-based REST API for the Coding Assessment Platform.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Local Setup](#2-local-setup)
3. [Environment Variables](#3-environment-variables)
4. [Database](#4-database)
5. [Authentication](#5-authentication)
6. [API Reference](#6-api-reference)
7. [Judge0 Integration](#7-judge0-integration)
8. [Anti-Cheat (Violations)](#8-anti-cheat-violations)
9. [Scoring & Session Lifecycle](#9-scoring--session-lifecycle)
10. [Admin Reports](#10-admin-reports)
11. [System Health Endpoints](#11-system-health-endpoints)
12. [Production Build (Docker)](#12-production-build-docker)

---

## 1. Project Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app factory, CORS, router registration
│   ├── dependencies.py       # Auth dependency injectors (require_candidate, require_admin)
│   ├── security.py           # JWT creation/decoding, bcrypt password hashing
│   ├── schemas.py            # Pydantic request/response models
│   ├── judge0_service.py     # Judge0 CE client (async, base64-encoded)
│   ├── db/
│   │   ├── database.py       # SQLAlchemy engine, session factory, DB URL builder
│   │   └── models.py         # ORM models + enums
│   ├── routes/
│   │   ├── auth.py           # /auth/login, /auth/refresh, /auth/logout
│   │   ├── skills.py         # /skills, /user/progress, /skills/{id}/levels, /user/badges
│   │   ├── sessions.py       # /sessions/* (start, detail, draft, run, submit, violation)
│   │   ├── submissions.py    # /submissions/{id}/results
│   │   ├── system.py         # /, /health, /judge0-smoke
│   │   └── admin/
│   │       ├── core.py       # /admin/stats, /admin/candidates, /admin/credentials, /admin/seed
│   │       └── reports.py    # /admin/reports/* (PDF, CSV, JSON)
│   └── services/
│       └── session_service.py # Business logic: problem selection, execution, scoring, badges
├── alembic/                  # Database migration scripts
│   └── versions/
├── scripts/                  # Utility scripts (seeding, resets)
├── Dockerfile                # Multi-stage production image
├── requirements.txt
├── alembic.ini
├── .env.example
└── DOCS.md                   # This file
```

---

## 2. Local Setup

### Prerequisites

- Python 3.11 or later
- PostgreSQL 13+ running and accessible
- A Judge0 CE endpoint (use `https://ce.judge0.com` for development)

### Steps

```bash
# 1. Navigate into the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows PowerShell
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and fill in DATABASE_URL, JUDGE0_BASE_URL, JWT_SECRET_KEY

# 5. Apply database migrations
alembic upgrade head

# 6. Start the development server
uvicorn app.main:app --reload --port 9515
```

> **Tip:** The interactive API docs are at [http://localhost:9515/docs](http://localhost:9515/docs) (Swagger UI).

---

## 3. Environment Variables

Copy `.env.example` to `.env` and fill in the values.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENV` | — | `development` | Set to `production` to restrict CORS and enable secure cookies |
| `CORS_ALLOWED_ORIGINS` | Prod only | — | Comma-separated list of allowed frontend origins |
| `DATABASE_URL` | ✅* | — | Full SQLAlchemy URL, e.g. `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `DB_HOST` | ✅* | `localhost` | Used when `DATABASE_URL` is not set |
| `DB_PORT` | — | `5432` | |
| `DB_NAME` | ✅* | `codingplatform` | |
| `DB_USER` | ✅* | `postgres` | |
| `DB_PASSWORD` | ✅* | `postgres` | |
| `DB_SECRET_ARN` | — | — | AWS Secrets Manager ARN; used to fetch `username` and `password` when not set directly |
| `JUDGE0_BASE_URL` | ✅ | `https://ce.judge0.com` | Base URL of the Judge0 CE instance |
| `JUDGE0_VERIFY_SSL` | — | `false` | Set to `true` to verify SSL for Judge0 (needed in some self-hosted setups) |
| `JWT_SECRET_KEY` | ✅ | `dev-only-insecure-secret` | **Change in production.** Secret used to sign JWTs. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | — | `15` | Lifetime of the short-lived access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | — | `7` | Lifetime of the long-lived refresh token (stored in httpOnly cookie) |
| `SCORE_PASS_THRESHOLD` | — | `70` | Minimum integer score (0–100) required to clear a level |
| `MAX_ATTEMPTS_PER_LEVEL` | — | `5` | How many times a candidate can attempt a given skill+level |

> *Either `DATABASE_URL` **or** the `DB_*` individual fields (or `DB_SECRET_ARN`) must be provided.

---

## 4. Database

### ORM & Migrations

- **ORM:** SQLAlchemy 2.x with declarative mapped classes (`app/db/models.py`).
- **Migrations:** Alembic (`alembic/`). The `sqlalchemy.url` in `alembic.ini` is intentionally blank — the `env.py` reads `DATABASE_URL` at runtime from the environment.

#### Common migration commands

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new auto-generated migration after editing models.py
alembic revision --autogenerate -m "describe your change"

# Roll back one migration
alembic downgrade -1

# View migration history
alembic history
```

## 5. Authentication

The API uses a **dual-token JWT** scheme:

| Token | Where stored | TTL | Purpose |
|-------|-------------|-----|---------|
| **Access token** | `Authorization: Bearer <token>` header | 15 min (default) | Authenticates every request |
| **Refresh token** | `httpOnly` cookie (`refresh_token`) | 7 days (default) | Issues new access tokens silently |

### Auth Endpoints

```
POST /auth/login     — email + password → access token + sets refresh cookie
POST /auth/refresh   — reads refresh cookie → new access token
POST /auth/logout    — clears the refresh cookie
```

### Protected Route Dependencies

```python
from app.dependencies import require_candidate, require_admin
```

Use as a FastAPI dependency to restrict access:

```python
@router.get("/my-endpoint")
def my_route(current_user: User = Depends(require_candidate)):
    ...
```

`require_candidate` → validates JWT, checks `role == candidate`  
`require_admin` → validates JWT, checks `role == admin`

---

## 6. API Reference

> Full interactive docs: `/docs` (Swagger) or `/redoc` (ReDoc).

### Auth (`/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | None | Login with email + password |
| POST | `/auth/refresh` | Cookie | Exchange refresh token for new access token |
| POST | `/auth/logout` | None | Clear refresh cookie |

### Skills (`/skills`, `/user`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/skills` | None | List all skills |
| GET | `/user/progress` | Candidate | Get skill+level progress for the logged-in candidate |
| GET | `/skills/{skill_id}/levels` | Candidate | Get level progress for a specific skill |
| GET | `/user/badges` | Candidate | List badges earned by the logged-in candidate |

### Sessions (`/sessions`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/sessions/start` | Candidate | Start a new assessment session |
| GET | `/sessions/{session_id}` | Candidate | Get session details + time remaining |
| POST | `/sessions/{session_id}/draft` | Candidate | Auto-save current code draft |
| POST | `/sessions/{session_id}/run` | Candidate | Run code against sample test cases |
| POST | `/sessions/{session_id}/submit` | Candidate | Submit final answers for grading |
| POST | `/sessions/{session_id}/violation` | Candidate | Log a proctoring violation event |

#### `POST /sessions/start` — Request body

```json
{
  "skill_id": "uuid",
  "level": "Beginner"
}
```

#### `POST /sessions/{id}/submit` — Request body

```json
{
  "answers": [
    { "problem_id": "uuid1", "code": "...", "language": "python" },
    { "problem_id": "uuid2", "code": "...", "language": "python" }
  ]
}
```

#### `POST /sessions/{id}/run` — Request body

```json
{
  "code": "...",
  "language": "python",
  "problem_id": "uuid",
  "use_hidden": false
}
```

### Submissions (`/submissions`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/submissions/{submission_id}/results` | Candidate | Get detailed results for a past submission |

### Admin (`/admin`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/stats` | Admin | Dashboard KPIs |
| GET | `/admin/candidates` | Admin | List candidates with filtering |
| GET | `/admin/credentials` | Admin | List candidates with verified skill credentials |

#### `GET /admin/candidates` — Query params

| Param | Type | Description |
|-------|------|-------------|
| `employee_id` | string | Partial match on employee ID |
| `years_min` / `years_max` | int | Filter by years at Indium |
| `exp_min` / `exp_max` | int | Filter by overall experience |

### Admin Reports (`/admin/reports`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/reports/{user_id}/json` | Admin | Full JSON report for a candidate |
| GET | `/admin/reports/{user_id}/pdf` | Admin | PDF report for a candidate |
| GET | `/admin/reports/{user_id}/csv` | Admin | CSV report for a candidate |
| GET | `/admin/reports/{user_id}/sessions` | Admin | List of sessions for a candidate |
| GET | `/admin/reports/{user_id}/sessions/{session_id}/json` | Admin | JSON report for one session |
| GET | `/admin/reports/{user_id}/sessions/{session_id}/pdf` | Admin | PDF report for one session |
| GET | `/admin/reports/{user_id}/sessions/{session_id}/csv` | Admin | CSV report for one session |
| POST | `/admin/reports/export/zip` | Admin | Bulk ZIP export (PDF or full mode) |

### System

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | None | API status and links |
| GET | `/health` | None | DB + Judge0 connectivity check |
| GET | `/judge0-smoke` | None | End-to-end execution test (Python, Java, JS, TypeScript) |

---

## 7. Judge0 Integration

The `Judge0Service` class (`app/judge0_service.py`) wraps the Judge0 CE REST API.

### Design Decisions

- **Always async** (`wait=false`): submissions are queued, then polled until a terminal status.
- **Always base64-encoded** (`base64_encoded=true`): avoids encoding issues with special characters in code and output.
- **Polling loop:** up to 40 attempts at 0.5 s intervals for single-file, 1.0 s for multi-file.

### Language IDs (used in the platform)

| Language | Judge0 ID | Monaco ID |
|----------|-----------|-----------|
| Python 3 | 71 | `python` |
| Java | 62 | `java` |
| JavaScript | 63 | `javascript` |
| TypeScript | 74 | `typescript` |
| SQLite | 82 | `sql` |
| Multi-file (Bash entrypoint) | 89 | varies |

### Execution Modes

#### Single-file (`execute`)

Used for `coding` and `sql` questions. Each test case is submitted as a separate Judge0 job. Results are aggregated.

- **SQL:** The candidate's query is prepended with the setup DDL from the test case's `input` field.
- **Pass criterion:** `status_id == 3` (Accepted) AND `stdout.strip() == expected_output.strip()`.

#### Multi-file (`execute_multifile`)

Used for `framework` questions. A ZIP archive is built containing:

- `run` — bash entrypoint (`pytest` for Python, `jest` for JS/TS)
- All `starter_files` provided by the problem
- The candidate's solution file(s)

The entire ZIP is submitted as `additional_files` with `language_id=89`.

### Status Mapping

| Judge0 status_id | Platform `ExecutionStatus` |
|-----------------|---------------------------|
| 3 | `success` |
| 4 | `wrong_answer` |
| 5 | `time_limit_exceeded` |
| 6 | `compile_error` |
| 7–14 | `runtime_error` |

---

## 8. Anti-Cheat (Violations)

The frontend fires `POST /sessions/{id}/violation` for every detected integrity event.

### Deduplication

The backend deduplicates identical violation types within a **2-second window** to prevent noisy bursts from a single event triggering multiple logs.

### Timestamp Validation

The backend accepts the client-supplied timestamp only if the clock drift between client and server is **≤ 5 minutes**. Otherwise it falls back to the server's `now()`.

### Violation Types

| Type | Trigger |
|------|---------|
| `tab_switch` | `document.visibilitychange` to hidden |
| `window_blur` | `window` blur event |
| `tab_switch_shortcut` | Alt+Tab / Cmd+Tab detected |
| `fullscreen_exit` | Fullscreen API exit |
| `paste` / `paste_attempt` | Clipboard paste in the editor |
| `copy` / `cut` | Clipboard copy/cut |
| `select_all` | Ctrl+A / Cmd+A |
| `devtools_shortcut` | F12, Ctrl+Shift+I, etc. |
| `context_menu` | Right-click |
| `visibility_hidden` | Page Visibility API |

---

## 9. Scoring & Session Lifecycle

### Session Start

1. Validate skill exists and level is unlocked for the candidate.
2. Check attempt count < `MAX_ATTEMPTS_PER_LEVEL`.
3. Fetch all problems for skill+level.
4. Call `choose_two_problems()` — selects 2 problems, preferring diversity by question type. The selection is seeded by `user_id + attempt_number` for reproducibility.
5. Create `AssessmentSession` with `expires_at = now + problem.time_limit_minutes`.
6. Store the two problem IDs as a JSON list in `last_draft_code` for session restoration.

### Submission Scoring

1. Each answer is routed to `execute_problem()`, which picks the right Judge0 mode (`execute` vs `execute_multifile`).
2. Results are averaged across both problems: `score = round(mean([score1, score2]))`.
3. If `score >= SCORE_PASS_THRESHOLD`: `SubmissionStatus.CLEARED`, otherwise `FAILED`.
4. On `CLEARED`:
   - `UserSkillProgress` for the current level is marked `cleared = True`.
   - The **next level** (if any) is unlocked in `UserSkillProgress`.
   - A **badge** is awarded via `award_level_badge()`.

### Session Expiry

The backend checks `expires_at <= now()` at every `GET /sessions/{id}`, `run`, and `submit` call. Expired sessions are immediately transitioned to `timed_out`.

---

## 10. Admin Reports

Reports are generated by `app/routes/admin/reports.py` using `xhtml2pdf` for PDF rendering.

### Output Formats

| Format | Content |
|--------|---------|
| JSON | Full structured data (sessions, submissions, violations, test cases) |
| PDF | Formatted report with candidate profile, session history, violation summary |
| CSV | Tabular data suitable for spreadsheet import |

### Bulk ZIP Export

`POST /admin/reports/export/zip` accepts a list of `user_ids` and a `mode`:

- `"latest"` — one report per candidate (their most recent session)
- `"full"` — all sessions for each candidate

Returns a ZIP archive of PDFs.

---

## 11. System Health Endpoints

### `GET /health`

Checks:
- **Database:** executes `SELECT 1`, measures latency.
- **Judge0:** calls `/languages`, measures latency and counts supported languages.

Returns `200` if all healthy, `503` if any service is down.

### `GET /judge0-smoke`

Submits tiny "print ok" programs in Python, Java, JavaScript, and TypeScript to Judge0 and checks execution results. Useful for verifying a new Judge0 deployment end-to-end.

---

## 12. Production Build (Docker)

The `Dockerfile` uses a two-stage build:

```
Stage 1 (builder): python:3.11-slim
  - Installs gcc/g++ and other build deps
  - pip install --user -r requirements.txt

Stage 2 (production): python:3.11-slim
  - Copies installed packages from builder
  - Exposes port 8000
  - CMD: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Build and run locally:

```bash
docker build -t coding-platform-backend .
docker run -p 8000:8000 --env-file .env coding-platform-backend
```

> In the full production stack, the Docker Compose file in `aws-infra/` manages the backend alongside PostgreSQL, Redis, and Judge0.
