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

## 3. Non-goal

No visual form builder and only one widget type (contact_form). The type column exists so more can be added later