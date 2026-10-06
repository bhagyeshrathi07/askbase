# AskBase

A multi-tenant document Q&A API. Users register, upload documents, and ask
questions over their own documents; answers stream back with citations to the
chunks they came from. Every tenant is isolated, every query is metered, and
repeat questions are served from cache.

Built as a production-style backend: FastAPI, PostgreSQL 16 + pgvector,
Redis, RQ workers, JWT + API-key auth, pytest in GitHub Actions, Docker
Compose, and a measured load test.

## Status

**Phase 0 (skeleton)** — FastAPI app with `/health`, Dockerfile, Compose
stack (app, Postgres + pgvector, Redis), settings from environment variables,
tests and CI. See the build guide in this folder for the remaining phases.

## Run it

```bash
docker compose up --build
```

Then:

```bash
curl -s localhost:8000/health
# {"status":"ok","postgres":true,"redis":true}
```

Interactive API docs: http://localhost:8000/docs

`docker compose watch` syncs `app/` into the container and restarts on change.
Stop everything with `docker compose down` (add `-v` to drop the database).

## Develop without Docker for the app

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # points at localhost; start db + redis via compose
docker compose up -d db redis
uvicorn app.main:app --reload
```

## Test and lint

```bash
pytest -q
ruff check .
```

The `/health` tests inject fake dependency checks, so they run with no
services up. CI runs the same two commands on every push and pull request.

## Configuration

| Variable       | Default                                                   | Purpose                      |
| -------------- | --------------------------------------------------------- | ---------------------------- |
| `ENVIRONMENT`  | `development`                                             | Environment label            |
| `DATABASE_URL` | `postgresql+asyncpg://askbase:askbase@localhost:5432/askbase` | SQLAlchemy async DSN     |
| `REDIS_URL`    | `redis://localhost:6379/0`                                | Cache, rate limits, queue    |

Settings are read from the environment first, then from a `.env` file if one
exists. Compose sets them for the containers; the defaults suit a local run
against the Compose database and Redis.

## Layout

```
app/
  config.py   settings (pydantic-settings)
  health.py   Postgres and Redis reachability checks
  main.py     application factory and /health
tests/
  test_health.py
compose.yaml  app + db (pgvector/pgvector:pg16) + redis
Dockerfile
.github/workflows/ci.yml
```
