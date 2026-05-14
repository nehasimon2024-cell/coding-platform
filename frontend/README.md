# Frontend — Developer Documentation

React 19 SPA for the Coding Assessment Platform.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Local Setup](#2-local-setup)
3. [Environment Variables](#3-environment-variables)
4. [Tech Stack](#4-tech-stack)
5. [Routing & Pages](#5-routing--pages)
6. [Authentication](#6-authentication)
7. [State Management](#7-state-management)
8. [Features](#8-features)
   - [Auth](#auth)
   - [Candidate](#candidate)
   - [Assessment](#assessment)
   - [Admin](#admin)
9. [API Layer](#9-api-layer)
10. [Anti-Cheat (Proctoring)](#10-anti-cheat-proctoring)
11. [Production Build (Docker + Nginx)](#11-production-build-docker--nginx)

---

## 1. Project Structure

```
frontend/
├── public/                   # Static assets
├── src/
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # Root component (QueryClient, Router, UserStore)
│   ├── index.css             # Global styles (Tailwind base)
│   ├── api/                  # Axios instance + interceptors
│   ├── components/
│   │   ├── layout/           # DashboardLayout (shared sidebar + header)
│   │   ├── ErrorBoundary.tsx
│   │   └── PageLoader.tsx    # Full-page loading spinner
│   ├── features/
│   │   ├── auth/             # Login page, ProtectedRoute, authService
│   │   ├── candidate/        # Dashboard, Badges, PastScores screens
│   │   ├── assessment/       # Instructions, AssessmentPage, ThankYou
│   │   └── admin/            # Overview, Candidates screens + adminService
│   ├── routes/
│   │   └── AppRoutes.tsx     # Centralized route definitions
│   ├── stores/
│   │   └── userStore.ts      # Zustand global user state
│   ├── types/
│   │   └── user.ts           # User type
│   └── lib/                  # Shared utilities (cn helper, etc.)
├── Dockerfile                # Multi-stage Nginx production image
├── nginx.conf                # Nginx SPA routing config
├── vite.config.ts
├── tsconfig.app.json
├── package.json
├── .env.example
└── DOCS.md                   # This file
```

---

## 2. Local Setup

### Prerequisites

- Node.js 20 or later
- npm 9+
- Backend running on `http://localhost:8000` (or wherever you point `VITE_API_URL`)

### Steps

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env
# Set VITE_API_URL=http://localhost:9515

# Start the dev server
npm run dev
```

App will be available at **http://localhost:9514** with hot module replacement (HMR).

### Other scripts

```bash
npm run build     # TypeScript compile + Vite production build → dist/
npm run preview   # Serve the production build locally
```

---

## 3. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ✅ | Base URL of the backend API, e.g. `http://localhost:9515` or `https://api.example.com` |

> Vite exposes only variables prefixed with `VITE_` to the browser bundle.

---

## 4. Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| React | 19 | UI framework |
| TypeScript | 5 | Type safety |
| Vite | 8 | Build tool + dev server |
| Tailwind CSS | 4 | Utility-first styling |
| shadcn/ui + Radix UI | — | Accessible component primitives |
| Lucide React | — | Icon set |
| Monaco Editor (`@monaco-editor/react`) | 4 | VS Code editor embedded in the browser |
| React Router DOM | 7 | Client-side routing |
| TanStack React Query | 5 | Server state, caching, background refetch |
| Axios | 1 | HTTP client |
| Zustand | 5 | Minimal global state store |
| Recharts | 3 | Charting (admin dashboard) |
| Geist font (`@fontsource-variable/geist`) | — | Typography |

---

## 5. Routing & Pages

All routes are defined in `src/routes/AppRoutes.tsx`. Every page component is **lazily loaded** using `React.lazy()` + `Suspense` to reduce initial bundle size.

### Route Map

```
/login                                  → Login (public)

/candidate/dashboard                    → DashboardPage (candidate only)
/candidate/badges                       → BadgesPage (candidate only)
/candidate/scores                       → PastScoresPage (candidate only)
/candidate/instructions                 → InstructionsPage (candidate only)
/candidate/assessment/:sessionId        → AssessmentPage (candidate only)
/candidate/thankyou                     → ThankYouPage (candidate only)

/admin/dashboard                        → OverviewPage (admin only)
/admin/candidates                       → CandidatesPage (admin only)

*                                       → Redirect to /login
```

### Access Control

`ProtectedRoute` wraps role-specific route groups. It reads the logged-in user's role from `useUserStore` and redirects to `/login` if:
- The user is not authenticated.
- The user's role does not match `allowedRoles`.

```tsx
<Route element={<ProtectedRoute allowedRoles={["candidate"]} />}>
  {/* candidate-only routes */}
</Route>
```

---

## 6. Authentication

### Login Flow

1. `Login.tsx` collects email + password and calls `POST /auth/login`.
2. Response includes `access_token`, `expires_in`, and `user` data.
3. The access token is stored in `useUserStore` (in-memory only — no localStorage).
4. The backend sets a `httpOnly` refresh cookie automatically.
5. React Query's Axios instance reads the token from the store on every request.

### Token Refresh

The Axios instance (`src/api/`) includes a **response interceptor** that:
1. Catches `401 Unauthorized` responses.
2. Calls `POST /auth/refresh` (the browser sends the httpOnly cookie automatically).
3. Updates the store with the new access token.
4. Retries the original request.

### Logout

`POST /auth/logout` is called, which instructs the backend to clear the refresh cookie. `useUserStore.clear()` is called on the client to wipe in-memory state, then the user is redirected to `/login`.

---

## 7. State Management

Global state is kept minimal using **Zustand** (`src/stores/userStore.ts`).

### `useUserStore`

```ts
type User = {
  id: string | null;
  name: string | null;
  role: "candidate" | "admin" | null;
  token: string | null;       // access token (in-memory only)
  department: string | null;
};

// Actions
setUser(user: User): void    // called after login / token refresh
clear(): void                // called on logout
```

> **Security note:** The access token is never persisted to `localStorage` or `sessionStorage`. It lives only in memory and is lost on page refresh. On refresh, the silent refresh flow (`/auth/refresh`) restores it using the httpOnly cookie, which is not accessible to JavaScript.

Server state (lists, sessions, etc.) is managed by **TanStack React Query** — each feature's service functions are wrapped in `useQuery` / `useMutation` hooks.

---

## 8. Features

### Auth

**Files:** `src/features/auth/`

| File | Description |
|------|-------------|
| `Login.tsx` | Login form with email/password inputs and error feedback |
| `ProtectedRoute.tsx` | Route guard HOC |
| `authService.ts` | `login()`, `refresh()`, `logout()` API calls |
| `SSOButton.tsx` | Reserved placeholder for SSO integration |

---

### Candidate

**Files:** `src/features/candidate/`

#### DashboardPage

- Fetches `GET /user/progress` to display a skill card grid.
- Each skill card shows 5 level nodes (Beginner → Specialist 2), colour-coded:
  - 🔒 Locked (not yet unlocked)
  - 🟡 Unlocked, not attempted or failed
  - ✅ Cleared
- Clicking an unlocked level navigates to `/candidate/instructions` with the skill+level in state.

#### BadgesPage

- Fetches `GET /user/badges`.
- Displays badge cards with name, description, criteria, and awarded date.

#### PastScoresPage

- Shows historical submission data with scores, status, and time taken per skill+level.

---

### Assessment

**Files:** `src/features/assessment/`

This is the most complex feature. The full candidate journey is:

```
DashboardPage → InstructionsPage → AssessmentPage → ThankYouPage
```

#### InstructionsPage

- Displays assessment rules, proctoring terms, and the skill+level selected.
- "Start Assessment" button calls `POST /sessions/start` and navigates to `AssessmentPage` with the `sessionId`.

#### AssessmentPage (`AssessmentPage.tsx`)

The core code editor experience. Key responsibilities:

| Concern | How it's handled |
|---------|-----------------|
| **Countdown timer** | Reads `seconds_remaining` from session response, local countdown interval |
| **Monaco editor** | Configured per question type. Language set by `allowed_languages` from the skill. |
| **Multi-problem tabs** | Session returns 2 problems; tab UI lets candidate switch between them |
| **Draft auto-save** | Periodically POSTs to `/sessions/{id}/draft` every ~30 s |
| **Run code** | POSTs to `/sessions/{id}/run`; displays test case results below the editor |
| **Submit** | Collects both answers, POSTs to `/sessions/{id}/submit`, navigates to ThankYou |
| **Proctoring** | Registers event listeners for violations; POSTs to `/sessions/{id}/violation` |
| **Session restore** | On mount, calls `GET /sessions/{id}` to restore code + timer if page was refreshed |

##### Question Type Rendering

The `AssessmentPage` renders a different editor UI based on `question_type`:

| Type | UI |
|------|----|
| `coding` | Monaco editor (single file) |
| `mcq` | Radio button list |
| `framework` | Monaco editor per starter file + file tabs |
| `sql` | Monaco editor with `sql` language mode |

#### ThankYouPage

Simple confirmation screen shown after a successful submission. Provides links back to the dashboard and scores.

---

### Admin

**Files:** `src/features/admin/`

#### OverviewPage (`/admin/dashboard`)

- Fetches `GET /admin/stats`.
- Displays KPI cards: Total Employees, Total Assessments, In Progress, Completed, Terminated.
- Charts (Recharts) for assessment trends.

#### CandidatesPage (`/admin/candidates`)

- Fetches `GET /admin/candidates` with optional filters.
- Data table: Name, Department, Skill, Score, Status, Submitted At.
- Per-row actions: view full report (PDF/JSON), download CSV.
- Filter panel: employee ID search, experience range sliders.

---

## 9. API Layer

### Axios Instance

Located in `src/api/`. A single Axios instance is created with:

- `baseURL` set from `VITE_API_URL`.
- **Request interceptor:** injects `Authorization: Bearer <token>` from `useUserStore`.
- **Response interceptor:** handles 401s with silent token refresh (see [Authentication](#6-authentication)).

### Service Modules

Each feature has its own service file for API calls:

| File | Endpoints covered |
|------|-------------------|
| `features/auth/authService.ts` | `/auth/*` |
| `features/candidate/candidateService.ts` | `/user/progress`, `/user/badges` |
| `features/assessment/services/` | `/sessions/*` |
| `features/admin/adminService.ts` | `/admin/*` |

---

## 10. Anti-Cheat (Proctoring)

The `AssessmentPage` installs event listeners when a session starts and removes them when the component unmounts.

### Events Monitored

| Browser Event | Violation Reported |
|--------------|-------------------|
| `document.visibilitychange` → hidden | `tab_switch` / `visibility_hidden` |
| `window.blur` | `window_blur` |
| `keydown` Alt+Tab / Cmd+Tab | `tab_switch_shortcut` |
| `fullscreenchange` (exit) | `fullscreen_exit` |
| `paste` on editor | `paste` |
| `copy` on editor | `copy` |
| `cut` on editor | `cut` |
| Ctrl+A / Cmd+A | `select_all` |
| F12 / Ctrl+Shift+I / Ctrl+Shift+J | `devtools_shortcut` |
| `contextmenu` | `context_menu` |

Each violation event is immediately posted to `POST /sessions/{id}/violation` with:
```json
{
  "type": "tab_switch",
  "timestamp": "2026-05-14T05:00:00.000Z",
  "metadata": { ... }
}
```

All violations are stored server-side and appear in admin reports.

---

## 11. Production Build (Docker + Nginx)

The `Dockerfile` uses a two-stage build:

```
Stage 1 (builder): node:20-alpine
  - npm install
  - npm run build → outputs to /app/dist

Stage 2 (production): nginx:stable-alpine
  - Copies dist/ to /usr/share/nginx/html
  - Uses custom nginx.conf
  - Exposes port 3000
```

The `nginx.conf` is configured for a React SPA — all requests that don't match a static file fall back to `index.html` so that client-side routing works correctly.

Build and run locally:

```bash
docker build -t coding-platform-frontend .
docker run -p 3000:3000 \
  -e VITE_API_URL=http://your-backend \
  coding-platform-frontend
```

> **Note:** `VITE_API_URL` is baked into the bundle at build time (Vite replaces `import.meta.env.VITE_API_URL` statically). You must rebuild the image if the backend URL changes.
