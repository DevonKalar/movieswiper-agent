# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`ms-agent` is a Flask microservice (the "Agent" service) for the MovieSwiper application. It handles chat conversations and integrates with MongoDB for persistence and Sentry for error tracking.

## Commands

**Install dependencies (including dev):**
```bash
poetry install
```

**Run tests:**
```bash
poetry run pytest
poetry run pytest tests/test_chat_routes.py  # single file
```

**Run development server:**
```bash
flask --app wsgi run
```

**Run production server:**
```bash
gunicorn -b 0.0.0.0:8000 wsgi:app --workers 2 --threads 4
```

**Docker:**
```bash
docker build -t ms-agent .
docker run -p 8000:8000 --env-file .env ms-agent
```

## Environment Variables

Copy `.env.example` to `.env`. Required vars:
- `MONGO_URL` — MongoDB connection string (db name is derived from this URL)
- `APP_ENV` — `development` or `production` (controls Flask debug mode)
- `SENTRY_DSN` — Sentry error tracking DSN
- `OPENAI_API_KEY` — OpenAI key (configured but not yet used)
- `JWT_SECRET` — HS256 secret used to verify access tokens

## Architecture

Flask app factory pattern (`app/__init__.py::create_app`) wires together:
1. Config (`app/config.py`) — `DevConfig`/`ProdConfig` selected via `APP_ENV`
2. MongoDB (`app/extensions.py`) — exposes module-level `mongo_client` and `mongo_db`
3. Blueprints (`app/api/__init__.py`) — registered with URL prefixes
4. Request context middleware (`app/common/request_context.py`) — attaches `X-Request-ID` and `X-User-ID` to Flask `g`
5. Error handlers + Sentry logging

**Layered structure per feature module** (e.g. `app/api/chat/`):
```
routes.py   → HTTP endpoints, request parsing, response formatting
services.py → business logic
repo.py     → MongoDB queries
schemas.py  → Pydantic v2 models
```

**Current endpoints:**
- `GET /health/` — health check
- `GET /chat/messages?conversationId=X&limit=50` — list messages
- `POST /chat/messages` — create message

**Auth** (`app/common/auth.py`): `require_auth` decorator extracts `Authorization: Bearer <token>`, decodes and validates the JWT (HS256, secret from `JWT_SECRET`), and sets `g.user` (`TokenPayload(sub, email)`). Raises `UnauthorizedError` on any failure. Apply to routes that need authentication:
```python
from app.common.auth import require_auth

@bp.get('/protected')
@require_auth
def protected():
    user_id = g.user.sub  # str
    email = g.user.email  # str | None
```

**Custom exception hierarchy** (`app/common/error_handler.py`): `AppError` → `NotFoundError` (404), `ValidationError` (400), `ConflictError` (409), `UnauthorizedError` (401). All serialize to `{message, error_code}` JSON and report to Sentry. Raise these (not `abort()`) from routes — the generic `Exception` handler intercepts HTTP exceptions and returns 500.

## Testing

Tests live in `tests/`. `conftest.py` patches `app.extensions.mongo_db` with a `MagicMock` before `create_app()` runs so no real MongoDB is needed. Route tests patch the service layer via `unittest.mock.patch`.

