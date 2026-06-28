# 🧥 Velour

**Your AI Personal Stylist** — Wardrobe management and outfit recommendation platform powered by AI.

Velour helps you organize your wardrobe digitally and receive personalized outfit recommendations based on your clothing, weather, and occasion. Decide what to wear today in under one minute.

---

## ✨ Features (MVP)

- **Digital Wardrobe** — Upload and organize your clothing items
- **AI Classification** — Automatic detection of category, color, pattern, and season
- **Smart Recommendations** — AI-powered outfit suggestions based on occasion and weather
- **Dashboard** — Weather, wardrobe summary, and today's recommendation at a glance

---

## 🏗️ Tech Stack

| Layer          | Technology                                  |
| -------------- | ------------------------------------------- |
| **Frontend**   | Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| **Backend**    | FastAPI, Python 3.12, Pydantic              |
| **Database**   | PostgreSQL 16                               |
| **Cache**      | Redis 7                                     |
| **Auth/BaaS**  | Supabase                                    |
| **Infra**      | Docker Compose, GitHub Actions              |
| **Tooling**    | pnpm workspaces, ESLint, Prettier, Husky    |

---

## 📁 Project Structure

```
velour/
├── apps/
│   └── web/                  # Next.js 15 frontend
├── services/
│   └── api/                  # FastAPI backend
├── packages/
│   └── types/                # @velour/types — shared TypeScript types
├── docs/                     # Documentation
├── infra/
│   └── docker/               # Docker configs (Postgres init, Nginx)
├── .github/
│   └── workflows/ci.yml      # GitHub Actions CI
├── docker-compose.yml        # Local development orchestration
└── package.json              # Root workspace config
```

---

## 📋 Prerequisites

- [Node.js](https://nodejs.org/) **≥ 22.0**
- [pnpm](https://pnpm.io/) **≥ 9.0** — `npm install -g pnpm`
- [Docker](https://www.docker.com/) & Docker Compose
- [Python](https://www.python.org/) **≥ 3.12** (for local backend development without Docker)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-org/velour.git
cd velour
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your Supabase credentials and other values
```

### 3. Install dependencies

```bash
pnpm install
```

### 4. Start everything with Docker Compose

```bash
docker compose up
```

This starts all services:

| Service      | URL                        |
| ------------ | -------------------------- |
| **Frontend** | http://localhost:3000       |
| **API**      | http://localhost:8000       |
| **API Docs** | http://localhost:8000/docs  |
| **Postgres** | `localhost:5432`           |
| **Redis**    | `localhost:6379`           |

### 5. (Alternative) Run services individually

```bash
# Frontend only
pnpm dev:web

# API only (requires Docker for Postgres/Redis)
docker compose up postgres redis -d
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 📜 Available Scripts

| Script              | Description                                |
| ------------------- | ------------------------------------------ |
| `pnpm dev`          | Start all dev servers in parallel           |
| `pnpm dev:web`      | Start Next.js dev server                    |
| `pnpm dev:api`      | Start FastAPI via Docker                    |
| `pnpm build`        | Build all packages and apps                 |
| `pnpm lint`         | Run ESLint across the workspace             |
| `pnpm lint:fix`     | Run ESLint with auto-fix                    |
| `pnpm format`       | Format all files with Prettier              |
| `pnpm format:check` | Check formatting without modifying files    |
| `pnpm typecheck`    | Run TypeScript type checking                |
| `pnpm docker:up`    | Start Docker Compose (detached)             |
| `pnpm docker:down`  | Stop Docker Compose                         |
| `pnpm docker:build` | Build Docker images                         |
| `pnpm docker:logs`  | Follow Docker Compose logs                  |

---

## 🧪 Development

### Code Quality

- **ESLint** — TypeScript linting with Prettier integration
- **Prettier** — Consistent code formatting
- **Ruff** — Python linting and formatting
- **Husky** — Git hooks run lint-staged on pre-commit
- **lint-staged** — Only lint/format staged files

### CI Pipeline

GitHub Actions runs on every push/PR to `main`:
1. Lint & format check
2. TypeScript type check
3. Build web app
4. Build & lint API
5. Docker image build

---

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Ensure `pnpm lint` and `pnpm format:check` pass
4. Submit a pull request

---

## 📄 License

Private — All rights reserved.
