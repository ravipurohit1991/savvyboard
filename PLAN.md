# Plan: SavvyBoard — Open-Source Product Feedback & Roadmap Platform

## Product Vision
Build a self-hosted, full-stack product management app that lets teams collect public/private user feedback, surface the most requested features through voting, manage a transparent public roadmap, and publish a changelog of shipped work.

**Why this gets traction:**
- Existing tools (Canny, Productboard, Frill, Beamer) charge $50–150+/mo per seat.
- Open-source projects and bootstrapped SaaS teams want a transparent feedback loop with their users.
- A polished, Docker-deployable alternative with a great README and screenshots fills a real gap.
- It is genuinely useful for product leads/managers and gives GitHub stars because teams can self-host it.

## Proposed Name
**SavvyBoard** (open to change). Alternatives: RoadPulse, InsightFlow, FeatureHub.

## Tech Stack
| Layer | Technology |
|-------|------------|
| Backend API | Python 3.11 + FastAPI |
| ORM / Models | SQLModel (Pydantic v2) |
| Database | PostgreSQL 15 |
| Migrations | Alembic |
| Auth | JWT access + refresh tokens (email/password), bcrypt |
| Frontend | React 18 + TypeScript |
| Build Tool | Vite |
| Styling | TailwindCSS + shadcn/ui components |
| Data Fetching | TanStack Query (React Query) |
| Routing | React Router v6 |
| Charts | Recharts |
| Testing | pytest (backend), Vitest (frontend) |
| Deployment | Docker + Docker Compose |

## Architecture (FastAPI full-stack template style)
```
new_app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── main.py              # FastAPI app factory
│   │   │   ├── deps.py              # auth & DB dependencies
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── workspaces.py
│   │   │       ├── boards.py
│   │   │       ├── feedback.py
│   │   │       ├── roadmap.py
│   │   │       └── changelog.py
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic Settings
│   │   │   ├── security.py          # passwords, tokens
│   │   │   └── logging.py
│   │   ├── crud/
│   │   │   ├── user.py
│   │   │   ├── workspace.py
│   │   │   ├── board.py
│   │   │   ├── feedback_item.py
│   │   │   ├── vote.py
│   │   │   └── changelog.py
│   │   ├── models/
│   │   │   └── *.py                 # SQLModel tables
│   │   ├── schemas/
│   │   │   └── *.py                 # Pydantic request/response schemas
│   │   ├── tests/
│   │   └── main.py                  # uvicorn entrypoint
│   ├── alembic/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/                     # generated/typed API clients
│   │   ├── components/              # shared UI + shadcn
│   │   ├── hooks/                   # TanStack Query hooks
│   │   ├── pages/                   # route pages
│   │   ├── routes/                  # React Router config
│   │   ├── types/                   # TypeScript interfaces
│   │   └── main.tsx
│   ├── index.html
│   ├── Dockerfile
│   ├── package.json
│   └── tailwind.config.js
├── scripts/
│   └── seed_demo.py                 # creates demo workspace + screenshots data
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

## MVP Feature Set
### Auth & Accounts
- Register / login with email + password (JWT).
- Refresh token rotation.
- Logged-in users can manage their profile.

### Workspaces
- A user creates a workspace (e.g. "Acme SaaS").
- Workspace slug for public pages (`/w/acme`).
- Members with roles: owner, admin, member.

### Feedback Boards
- Public or private boards per workspace.
- Anyone can view public boards; only logged-in users submit/vote.
- Feedback item: title, description, category, status, vote count, comment count.
- Categories: Feature, Bug, Improvement, Integration.
- Voting (one vote per user per item).
- Comments on items.

### Roadmap
- Admin can move feedback items into roadmap columns:
  - Under Review, Planned, In Progress, Shipped, Closed.
- Public roadmap page rendered as a Kanban-style board.

### Changelog
- When an item is marked Shipped, the admin can publish a changelog entry.
- Public changelog page (`/w/acme/changelog`).
- Rich text-ish description (markdown support).

### Admin Dashboard
- Metrics cards: total feedback, votes, shipped items, comments.
- Recent activity feed.
- Charts: feedback by category, top voted items.

### Public Pages
- Clean, responsive public portal:
  - Workspace home / boards list
  - Feedback board with submit/vote
  - Roadmap
  - Changelog

### Demo Data & Screenshots
- A seed script creates a realistic demo workspace (`DemoStartup`) with:
  - 3 boards, 30+ feedback items, realistic votes/comments
  - A populated roadmap and changelog
- README will include 4–6 screenshots of the public portal and admin dashboard.

## Quality & GitHub Readiness
- `.env.example` with zero secrets.
- Docker Compose for one-command local start.
- Backend tests with pytest.
- Frontend tests with Vitest.
- Pre-commit hooks config (optional but nice).
- MIT LICENSE.
- Comprehensive README with:
  - Elevator pitch & screenshots
  - Features list
  - Quick start (Docker)
  - Local dev setup
  - Tech stack
  - API docs note (auto-generated by FastAPI)
  - Contributing note
  - Author: Ravi Purushottam, GitHub: ravipurohit1991
  - No API keys or personal paths in code.

## Open Questions for Approval
1. Is the name **SavvyBoard** OK, or do you prefer another?
2. Should the public feedback portal allow anonymous submissions, or require login for everything except viewing?
3. Are you happy with the FastAPI + React/TS stack, or do you want a different frontend (e.g., Next.js)?

## Implementation Phases
1. Project scaffolding (backend & frontend skeleton, Docker, DB).
2. Auth system + users.
3. Workspace + board CRUD.
4. Feedback items + voting + comments.
5. Roadmap + changelog.
6. Admin dashboard + charts.
7. Public pages styling.
8. Demo seed data + screenshots.
9. README, LICENSE, final polish.
