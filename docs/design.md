# Design: Embeddable Widget & Lead-Capture Platform

## 1. Problem

Customers (widget owners) need to put a lead-capture form on any website
without building a backend. An owner creates a widget through an
authenticated API and gets back a one-line `<script>` snippet. When a visitor
on the owner's site fills in the form, the submission goes to this backend,
where it is validated, checked for abuse, enriched with geo data, stored, and
shown to the owner in a dashboard.

Two kinds of users:

- **Owner**: authenticated (Supabase Auth). Manages widgets, reads submissions
  and stats. Can only ever see their own data.
- **Visitor**: anonymous, on a site we don't control. Loads the widget and
  submits the form. Their input is untrusted.

Three request paths, kept separate:

1. Owner -> Widget management + dashboard API (authenticated)
2. Customer site -> `widget.js` and `GET /widgets/{id}/config` (public, cached, CORS)
3. Visitor -> `POST /submissions` (public, CORS, validated, rate limited)

## 2. Data model

### widgets

| Column | Type | Notes |
|---|---|---|
| id | text (short random, e.g. 10 chars) | Public ID used in the embed snippet. Not guessable or sequential. Primary key. |
| owner_id | uuid | Supabase user ID. Every query filters on it. |
| type | text | `contact_form` for now (see non-goal) |
| title | text | |
| description | text | |
| fields | jsonb | List of `{name, label, type, required}` |
| button_text | text | |
| is_active | boolean | Inactive widgets reject submissions |
| config_version | integer | Bumped on every edit, used for cache-busting |
| created_at, updated_at | timestamptz | |

Indexes: `(owner_id)`.

### submissions

| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key |
| widget_id | text | FK -> widgets.id |
| owner_id | uuid | Copied from the widget at insert time, so tenant filters never need a join |
| data | jsonb | Validated form values |
| ip_address | text | Used for rate limiting and geo lookup |
| country, city | text, nullable | Null if every geo provider failed |
| geo_provider | text, nullable | Which provider answered (useful evidence for the fallback proof) |
| idempotency_key | text, nullable | Client-generated per form render |
| notification_status | text | `pending` / `sent` / `failed`. Records the side-effect result without affecting the response. |
| created_at | timestamptz | |

Indexes:

- `(owner_id, created_at DESC)` for the dashboard
- `(widget_id, created_at DESC)` for per-widget stats
- Unique `(widget_id, idempotency_key)` so a retried POST stores once

### Tenant isolation rule

Every owner-facing query includes `owner_id = <authenticated user>`. A widget
that belongs to another owner returns 404, not 403, so IDs can't be probed.

### Schema management

Alembic migrations, not `create_all()`.

## 3. API contracts

Error shape for every endpoint (flat, no wrapper):
`{"error": "message"}`, plus `{"error": "...", "fields": {...}}` for validation errors.

### 3a. Owner API (authenticated, `Authorization: Bearer <jwt>`)

| Method | Path | Success | Errors |
|---|---|---|---|
| POST | /widgets | 201 + widget (includes `embed_snippet`) | 400 invalid body, 401 |
| GET | /widgets | 200 + list (own widgets only) | 401 |
| GET | /widgets/{id} | 200 + widget | 401, 404 |
| PUT | /widgets/{id} | 200 + widget (bumps `config_version`) | 400, 401, 404 |
| DELETE | /widgets/{id} | 204 | 401, 404 |
| GET | /dashboard/submissions?widget_id=&limit=&offset= | 200 + list | 401 |
| GET | /dashboard/stats | 200 + `{total, per_widget, per_day, per_country}` | 401 |

### 3b. Delivery (public, CORS `*`, cached)

| Method | Path | Notes |
|---|---|---|
| GET | /widget.v1.js | The script. `Cache-Control: public, max-age=31536000, immutable`. New release = new filename. |
| GET | /widget.js?id=abc123 | The URL in the embed snippet. Short-lived redirect or loader to the current versioned bundle (`max-age=300`). |
| GET | /widgets/{id}/config | Public fields only (title, fields, button text). `Cache-Control: public, max-age=60`. 404 if missing or inactive. |

### 3c. Submission (public, CORS, protected)

`POST /submissions`

Body: `{"widget_id": "...", "data": {...}, "idempotency_key": "...", "website": ""}`
(`website` is the honeypot, hidden in the form and always empty for humans.)

| Case | Response |
|---|---|
| Valid | 201 `{"id": "..."}` |
| Repeat of same idempotency key | 200 with the original id, no second row |
| Malformed or missing fields | 400 |
| Body over size limit (e.g. 10 KB) | 413 |
| Unknown or inactive widget | 404 |
| Honeypot filled | 201 `{"id": "..."}` with nothing stored (silent drop, identical to success so a bot learns nothing) |
| Over rate limit | 429 + `Retry-After` |

`OPTIONS /submissions` answers the CORS preflight.

Processing order: size check -> rate limit -> validate -> honeypot -> idempotency check -> geo enrichment (A -> B -> none) -> store -> side effect in background (failure sets `notification_status = failed`, never changes the response).

## 4. Layers

```
app/
  main.py          app setup, CORS, routers, error handlers
  routes/          HTTP only: parse request, call service, shape response
    widgets.py  delivery.py  submissions.py  dashboard.py
  services/        business logic, no FastAPI imports
    widget_service.py  submission_service.py  geo.py  notifier.py
  repositories/    all SQL, every query takes owner_id where relevant
  schemas/         Pydantic request/response models
  core/            config (env), auth dependency, rate limiter
migrations/        Alembic
```

Rule: routes never touch the database, repositories never raise HTTP errors.

## 5. Non-goal

No visual form builder; only the contact_form widget type.

## 6. Changes made while building

- Honeypot returns 201 (not 200) so a bot cannot tell it was caught.
- Rate limiting is an in-memory per-IP dependency that runs before validation, so every request counts. Per-widget limits are not implemented.
- A missing Content-Length on `POST /submissions` returns 411, so the 10 KB limit cannot be bypassed.
- `notification_status` can also be `skipped` (the widget has no email field).
- `AUTH_MODE=demo` accepts two fixed evaluation tokens so a reviewer can run the system without a Supabase account. Supabase remains the real auth path.
- The API runs in Docker Compose and applies migrations on start.
