# Embeddable Widget & Lead-Capture Platform

FlyRank Internship, Backend Track capstone.

A customer creates a lead-capture widget through an authenticated API and pastes one `<script>` tag on any website. Visitors submit the form to a public API that validates the payload, rate limits and spam-filters it, enriches it with location data, stores it, and shows it to the widget's owner in a dashboard.

Stack: Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker Compose. Everything is free and runs locally.

## Architecture

```text
Widget owner (authenticated)
  -> /widgets            widget CRUD         -> Postgres: widgets (isolated by owner_id)
  -> /dashboard/*        submissions, stats  <- Postgres: submissions

Customer website (any origin)
  <script src="http://localhost:8000/widget.js?id=abc123"></script>
  -> GET /widget.js            302 to the versioned bundle (cache 5 min)
  -> GET /widget.v1.js         the script (cache 1 year, immutable)
  -> GET /widgets/{id}/config  public config (cache 60 s, CORS)

Website visitor
  -> POST /submissions         public, CORS
       1. size limit               too big          -> 413
       2. per-IP rate limit        flood            -> 429 + Retry-After
       3. validation               bad payload      -> 400
       4. honeypot                 bot              -> looks successful, nothing stored
       5. idempotency check        retry            -> original id, no second row
       6. geo enrichment           provider A -> provider B -> none (never fails the request)
       7. store the row
       8. background job           confirmation email, 3 attempts; failure only sets
                                   notification_status = failed
```

Code layers: `routes/` (HTTP only) -> `services/` (business logic) -> `repositories/` (all SQL). `schemas/` holds the Pydantic models and `core/` holds config, auth, database, and the rate limiter. Schema changes are Alembic migrations in `migrations/`.

## Quick start

Requires Docker with Compose v2.

```bash
git clone https://github.com/Swathy-S-08/flyrank-capstone-widgetplatform.git
cd flyrank-capstone-widgetplatform
cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env
docker compose up --build -d --wait
docker compose exec api python -m app.seed
```

The API is at http://localhost:8000 and interactive docs at http://localhost:8000/docs. Migrations run automatically when the API container starts. The seed command is safe to run more than once.

### Demo login (evaluation mode)

`.env.example` sets `AUTH_MODE=demo`, which accepts two fixed tokens so you can try the owner API without any account:

| Token | Owner | Seeded widget |
|---|---|---|
| `demo-owner-1` | tenant 1 | `demo-contact` (plus 6 sample submissions) |
| `demo-owner-2` | tenant 2 | `demo-other` |

```bash
curl -H "Authorization: Bearer demo-owner-1" http://localhost:8000/widgets
curl -H "Authorization: Bearer demo-owner-1" http://localhost:8000/dashboard/stats
curl -i -H "Authorization: Bearer demo-owner-1" http://localhost:8000/widgets/demo-other   # 404: other tenant
```

For real logins set `AUTH_MODE=supabase` plus `SUPABASE_URL` and `SUPABASE_ANON_KEY` (the anon/publishable key, never the service key). The bearer token is then a Supabase access token and the owner id is the Supabase user id.

### See the widget on a different origin

```bash
cd test-site
python -m http.server 5500 --bind 127.0.0.1
```

Open http://127.0.0.1:5500/. The page (port 5500) loads the widget from the API (port 8000) and submits cross-origin.

## API

All errors are flat JSON: `{"error": "message"}`, plus `"fields": {...}` for validation errors.

| Method and path | Auth | Success | Errors |
|---|---|---|---|
| `POST /widgets` | owner | 201, includes `embed_snippet` | 400, 401 |
| `GET /widgets` | owner | 200, own widgets only | 401 |
| `GET /widgets/{id}` | owner | 200 | 401, 404 |
| `PUT /widgets/{id}` | owner | 200, bumps `config_version` | 400, 401, 404 |
| `DELETE /widgets/{id}` | owner | 204 | 401, 404 |
| `GET /widgets/{id}/config` | public | 200, `Cache-Control: public, max-age=60` | 404 |
| `GET /widget.js?id={id}` | public | 302 to `/widget.v1.js`, `max-age=300` | |
| `GET /widget.v1.js` | public | 200, `max-age=31536000, immutable` | |
| `POST /submissions` | public, CORS | 201 `{"id"}`, or 200 for an idempotent replay | 400, 404, 411, 413, 429 |
| `GET /dashboard/submissions` | owner | 200, paged: `widget_id`, `limit` (1-100), `offset` | 400, 401 |
| `GET /dashboard/stats` | owner | 200: total, per widget, per day (`days`, 1-365), per country | 400, 401 |

`POST /submissions` body: `{"widget_id": "...", "data": {"email": "...", "message": "..."}, "idempotency_key": "optional", "website": ""}`. The `website` field is the honeypot and must stay empty.

Requests from other tenants get 404, never 403, so widget ids cannot be probed.

## Reproducing the resilience probes

Switches live in `.env`. After changing one, recreate the API: `docker compose up -d --force-recreate api`.

| Scenario | Settings | Expected |
|---|---|---|
| Provider A down, B answers | `GEO_MOCK=true`, `GEO_A_DOWN=true` | 201, row has `geo_provider = ipapi.co` |
| All providers down | also `GEO_B_DOWN=true` | 201, row stored with no location |
| Email side effect fails | `NOTIFY_FAIL=true` | 201 immediately, 3 logged retries, `notification_status = failed`, row stored |
| Rate limit | 15 rapid `POST /submissions` | first 10 pass, then 429 with `Retry-After` |

`GEO_MOCK=true` replaces the two real providers with deterministic mocks so the fallback proof does not depend on third-party uptime. With `GEO_MOCK=false` the real free APIs (ip-api.com, then ipapi.co) are used, but private and loopback addresses such as Docker's gateway have no location.

Evidence for every requirement, with real output, is in [EVIDENCE.md](EVIDENCE.md). The design document is [docs/design.md](docs/design.md) and AI usage is logged in [BUILDLOG.md](BUILDLOG.md).

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | see `.env.example` | Database credentials; Compose builds the in-container URL from them |
| `DATABASE_URL` | local URL | Only used when running the API outside Docker |
| `AUTH_MODE` | `supabase` in code, `demo` in `.env.example` | `demo` or `supabase` |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY` | empty | Needed only in supabase mode |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Used in the embed snippet |
| `RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS` | 10 and 10 | Per-IP limit on `POST /submissions` |
| `GEO_MOCK`, `GEO_A_DOWN`, `GEO_B_DOWN`, `GEO_TEST_IP` | off | Test switches for the geo fallback |
| `NOTIFY_FAIL` | off | Forces the email side effect to fail |

Secrets live only in `.env`, which is git-ignored.

## Scope and limitations

Non-goal: there is no visual form builder, and `contact_form` is the only widget type (the `type` column leaves room for more).

- The rate limiter is in memory and per process: it resets on restart and is not shared between workers. It limits per IP only; per-widget limiting is not implemented.
- The client IP is taken from the connection. Behind a reverse proxy this would need trusted forwarded headers.
- The background job uses FastAPI `BackgroundTasks`, which run in the same process. Retries are not persisted, so a crash mid-retry would leave a row as `pending`. A real queue (Celery, RQ) would fix that.
- The confirmation email is simulated with a console log.
- `AUTH_MODE=demo` uses static tokens and is for evaluation only. Never enable it in production.
- CORS is open to all origins on every route. The owner API uses bearer tokens, not cookies, so this does not expose sessions.
- The widget script is plain, unminified JavaScript. Config can be up to 60 seconds stale because of its cache header.
- The widget generates one idempotency key per page load, so a retried click is stored once.
- Geo lookups use free tiers with a 2 second timeout. Their rate limits and uptime are outside this project's control.
- There is no automated test suite. Behavior is verified by the scripted requests captured in EVIDENCE.md.
