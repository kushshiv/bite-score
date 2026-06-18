# BiteScore MVP

Food trust and transparency platform — structured hygiene observations, evidence-backed reviews, and transparent scoring.

## Prerequisites

Install these before running locally:

| Tool | Install |
|------|---------|
| **Node.js 20** | `nvm install 20 && nvm use 20` |
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ |
| **Poetry** | `curl -sSL https://install.python-poetry.org \| python3 -` |
| **Python 3.11+** | `brew install python@3.11` (if needed) |

Verify:

```bash
node --version    # v20.x
docker --version
poetry --version
python3 --version # 3.11+
```

## Quick start

### Using Make (recommended)

```bash
make install    # install backend + frontend deps
make up         # start PostgreSQL
make db-setup   # run migrations + load demo data
make dev        # shows how to start both servers
```

Then in two terminals:

```bash
make backend    # http://localhost:8000/docs
make frontend   # http://localhost:3000
```

Run `make help` for all commands.

### Manual setup

#### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Backend setup

```bash
cd backend
cp ../.env.example .env
poetry install --with dev
poetry run alembic upgrade head   # create schema
poetry run seed                   # load demo data
poetry run uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Frontend setup

```bash
cd frontend
npm install
NUXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

App: http://localhost:3000

## Demo accounts

All demo accounts use password: `Demo1234!`

| Email | Role |
|-------|------|
| admin@bitescore.demo | Admin |
| owner@bitescore.demo | Business owner |
| user@bitescore.demo | User |
| moderator@bitescore.demo | Moderator |

## Seed data

- 30 businesses across Berlin, Mumbai, and Austin
- 100 structured reviews
- Categories, badges, and sample claim requests

Re-seed (only if DB is empty):

```bash
make seed
# or: cd backend && poetry run seed
```

Reset database and re-seed from scratch:

```bash
make reset-db   # wipes volume, runs migrations, then seeds
```

## Database migrations

Schema changes are managed with **Alembic** — not `create_all()` on startup.

| Command | When |
|---------|------|
| `make migrate` | Apply pending migrations locally |
| `make db-setup` | Migrate + seed (first-time setup) |
| `poetry run alembic revision --autogenerate -m "describe change"` | Create a new migration after model changes |
| `poetry run alembic upgrade head` | Apply migrations |
| `poetry run alembic downgrade -1` | Roll back one revision |

Migrations run automatically:
- **Local dev:** `make backend` and `make seed` run migrations first
- **CI:** backend tests and a dedicated `migrations.yml` workflow
- **Docker deploy:** `migrate` service runs before `api` starts (`docker-compose.prod.yml`)
- **Container entrypoint:** API image runs `alembic upgrade head` before Uvicorn

If you previously used the empty placeholder migration, reset locally:

```bash
make reset-db
```

## Project structure

```
bite-score/
├── Makefile           # common dev commands (make help)
├── .github/workflows/ # GitHub Actions CI
├── frontend/          # Nuxt 3 + Tailwind + Pinia + Zod
│   └── tests/         # vitest unit tests
├── backend/           # FastAPI + SQLAlchemy + Alembic
│   └── tests/         # pytest API + unit tests
├── docker-compose.yml       # PostgreSQL 16 (local dev)
├── docker-compose.prod.yml  # Postgres + migrate job + API (deploy)
├── backend/Dockerfile       # API image with predeploy migrations
├── .github/workflows/       # CI + migration verification
└── .env.example
```

## API overview

| Endpoint | Description |
|----------|-------------|
| `POST /auth/register` | Create account |
| `POST /auth/login` | Get JWT token |
| `GET /businesses` | Search/list with filters |
| `GET /businesses/{slug}` | Business trust profile |
| `POST /reviews` | Submit structured observation |
| `POST /flags` | Report concern |
| `GET /admin/moderation-queue` | Moderation dashboard |
| `GET /billing/status` | Mocked Stripe billing |

## Scoring methodology

- 30% hygiene/cleanliness
- 20% food handling
- 15% staff hygiene
- 10% packaging
- 10% water safety confidence
- 10% evidence credibility
- 5% consistency weighting

Scores are platform-derived community signals, not government certifications.

## Testing

```bash
make test              # run all tests
make test-backend      # pytest only
make test-frontend     # vitest only
make lint              # backend ruff lint
```

If backend tests fail with `Command not found: pytest`, install dev dependencies:

```bash
cd backend && poetry install --with dev
```

### Backend tests (`backend/tests/`)

- `test_security.py` — password hashing, JWT encode/decode
- `test_scoring.py` — scoring engine and trust indicators
- `test_api_auth.py` — register, login, `/auth/me`
- `test_api_businesses.py` — list, search, business profiles
- `test_api_reviews.py` — review submission, billing mock

Uses PostgreSQL (same as local dev and production). Start Postgres and apply migrations first:

```bash
make up           # docker compose postgres
make migrate      # alembic upgrade head
make test-backend
```

### Frontend tests (`frontend/tests/`)

- `schemas.test.ts` — Zod validation for login, review, flag forms
- `auth.store.test.ts` — Pinia auth store roles and session
- `useAuthModal.test.ts` — modal open/close state

---

## Deployment

### Overview

| Component | Local dev | Production (AWS MVP) |
|-----------|-----------|----------------------|
| Frontend | `npm run dev` (:3000) | Nuxt build + Node or static behind Nginx |
| Backend | `uvicorn` (:8000) | Uvicorn/Gunicorn on EC2 |
| Database | Docker Postgres | RDS PostgreSQL (recommended) or Docker on EC2 |
| Uploads | Local `backend/uploads/` | S3 bucket |
| TLS | — | Nginx + Let's Encrypt or ALB |

### Option A: AWS EC2 (Terraform scaffold)

**Prerequisites:** AWS CLI configured, Terraform installed.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit: aws_region, db_password, instance_type
terraform init
terraform plan
terraform apply
```

Note the output `ec2_public_ip`.

**On the EC2 instance (SSH as ec2-user):**

```bash
# 1. Install runtime dependencies
sudo yum update -y
sudo yum install -y docker git
sudo systemctl enable docker && sudo systemctl start docker
sudo usermod -aG docker ec2-user

# 2. Install Docker Compose plugin + Node + Poetry (or use pre-built images)
# 3. Clone your repo
git clone <your-repo-url> bite-score && cd bite-score

# 4. Configure environment
cp .env.example backend/.env
# Set production values:
#   DATABASE_URL=postgresql+psycopg2://user:pass@<rds-host>:5432/bitescore
#   JWT_SECRET=<long-random-secret>
#   CORS_ORIGINS=https://yourdomain.com
#   API_BASE_URL=https://api.yourdomain.com

# 5. Database migrations + seed
cd backend && poetry install
poetry run alembic upgrade head
poetry run seed

# 6. Backend (migrations also run via Docker entrypoint in production images)
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 7. Frontend (separate process or build)
cd ../frontend && npm install && npm run build
NUXT_PUBLIC_API_BASE=https://api.yourdomain.com node .output/server/index.mjs
```

**Recommended production hardening:**
- Use **RDS PostgreSQL** instead of Docker Postgres (uncomment `aws_db_instance` in `terraform/main.tf`)
- Put **Nginx** in front of frontend (:80/:443) and proxy `/api` to backend :8000
- Restrict security group: remove public access to :8000 and :3000; only expose :80/:443
- Set a strong `JWT_SECRET` and rotate it periodically
- Move uploads to **S3** (update `UPLOAD_DIR` / storage service)

### Option B: Docker Compose on a single VPS

Works on EC2, DigitalOcean, Hetzner, etc. The `migrate` service runs as a **predeploy job** before the API container starts.

```bash
# On the server
git clone <your-repo-url> bite-score && cd bite-score
cp .env.example backend/.env
# Edit backend/.env for production (DATABASE_URL, JWT_SECRET, CORS_ORIGINS, ...)

# Start Postgres, run migrations, then API
docker compose -f docker-compose.prod.yml up --build -d

# Optional: seed demo data (first deploy only)
docker compose -f docker-compose.prod.yml exec api poetry run seed

cd ../frontend
npm install && npm run build
NUXT_PUBLIC_API_BASE=http://<server-ip>:8000 node .output/server/index.mjs
```

Run migrations only (e.g. before a rolling deploy):

```bash
make docker-migrate
# or: docker compose -f docker-compose.prod.yml run --rm migrate
```

### Option C: Frontend static + API only

If you only need a demo without SSR:

```bash
cd frontend
NUXT_PUBLIC_API_BASE=https://api.yourdomain.com npm run generate
# Serve frontend/.output/public via Nginx or S3 + CloudFront
```

### Post-deploy checklist

- [ ] `alembic upgrade head` completed successfully (or `migrate` service exited 0)
- [ ] `GET /health` returns `{"status":"ok"}`
- [ ] Frontend loads and can search businesses
- [ ] Login works with a seeded or registered account
- [ ] `CORS_ORIGINS` matches your frontend URL
- [ ] `JWT_SECRET` is not the default from `.env.example`
- [ ] Database backups enabled (RDS automated backups)
- [ ] HTTPS enabled on public endpoints

### Environment variables (production)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Long random secret for token signing |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `API_BASE_URL` | Public backend URL (for upload links) |
| `NUXT_PUBLIC_API_BASE` | Frontend → backend API URL |
| `UPLOAD_DIR` | Local path or migrate to S3 |
| `STRIPE_SECRET_KEY` | When billing is implemented |

---

## Environment variables (local)

Copy `.env.example` to `backend/.env` and adjust:

- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — Change to a long random string in production
- `CORS_ORIGINS` — Frontend URL(s)
- `UPLOAD_DIR` — Local upload directory

Frontend uses `NUXT_PUBLIC_API_BASE` (default: `http://localhost:8000`).

---

## Push to GitHub

### 1. Create a GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it e.g. `bite-score`
3. Choose **Private** or **Public**
4. Do **not** add a README, `.gitignore`, or license (this repo already has them)
5. Click **Create repository**

### 2. Initialize git and push (first time)

From the project root:

```bash
cd /Users/shivendra/personal-projects/bite-score

git init
git add .
git commit -m "Initial commit: BiteScore MVP with tests and CI"

# Replace YOUR_USERNAME and YOUR_REPO with your GitHub details
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Using SSH instead:

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3. Verify CI is running

After the first push, open your repo on GitHub → **Actions** tab.

You should see the **CI** workflow running two jobs:
- **Backend tests & lint** — `ruff` + `pytest`
- **Frontend tests** — `vitest`

CI runs automatically on every push and pull request to `main` / `master`.

### 4. Day-to-day workflow

```bash
git add .
git commit -m "Describe your change"
git push
```

---

## CI/CD pipeline

Workflow file: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

| Job | What it runs |
|-----|----------------|
| `backend` | `poetry install --with dev` → `ruff check` → `pytest` |
| `frontend` | `npm ci` → `npm test` |

**Triggers:** push and pull requests to `main` or `master`.

**Requirements:** Postgres must be running for backend tests. CI provisions PostgreSQL 16 automatically. No secrets required for the test suite.

To run the same checks locally before pushing:

```bash
make test
make lint
```

---

## Legal pages

- `/terms` — Terms of Service
- `/privacy` — Privacy Policy (GDPR-aware)
- `/moderation` — Content Moderation Policy + business appeal flow

## License

Proprietary — BiteScore MVP.
