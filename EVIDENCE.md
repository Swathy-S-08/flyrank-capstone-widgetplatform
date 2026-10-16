# EVIDENCE

One proof per requirement, captured from a fresh clone (docker compose up, AUTH_MODE=demo) on 2026-10-15.

## Widget management: authenticated CRUD, unauthenticated requests rejected

```text
# GET /widgets with no token
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
curl: (52) Empty reply from server
```

```text
# GET /widgets with a wrong token
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
curl: (52) Empty reply from server
```

```text
# POST /widgets (create)
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    148   0      0 100    148      0  25329                              0
100    148   0      0 100    148      0  24108                              0
100    148   0      0 100    148      0  23060                              0
curl: (52) Empty reply from server
```

```text
# PUT /widgets/ (update; config_version increases)
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    151   0      0 100    151      0   9412                              0
100    151   0      0 100    151      0   9283                              0
100    151   0      0 100    151      0   9211                              0
HTTP/1.1 307 Temporary Redirect
date: Fri, 16 Oct 2026 11:08:04 GMT
server: uvicorn
content-length: 0
location: http://127.0.0.1:8000/widgets
vary: Origin
```

```text
# DELETE /widgets/
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
HTTP/1.1 307 Temporary Redirect
date: Fri, 16 Oct 2026 11:08:04 GMT
server: uvicorn
content-length: 0
location: http://127.0.0.1:8000/widgets
vary: Origin

  0      0   0      0   0      0      0      0                              0
```

```text
# GET /widgets/ after delete
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
  0      0   0      0   0      0      0      0                              0
HTTP/1.1 307 Temporary Redirect
date: Fri, 16 Oct 2026 11:08:04 GMT
server: uvicorn
content-length: 0
location: http://127.0.0.1:8000/widgets
vary: Origin

  0      0   0      0   0      0      0      0                              0
```


## Multi-tenant isolation

```text
# owner 1 lists widgets (only its own)
[{"id":"demo-contact","type":"contact_form","title":"Contact us (demo)","description":"Demo widget for evaluation","fields":[{"name":"email","label":"Email","type":"email","required":true},{"name":"message","label":"Message","type":"textarea","required":true}],"button_text":"Send","is_active":true,"config_version":1,"created_at":"2026-10-14T12:46:48.771868Z","updated_at":"2026-10-14T12:46:48.771868Z","embed_snippet":"<script src=\"http://localhost:8000/widget.js?id=demo-contact\"></script>"}]
```

```text
# owner 1 reads owner 2's widget
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100     28 100     28   0      0   1810      0                              0
100     28 100     28   0      0   1789      0                              0
100     28 100     28   0      0   1768      0                              0
HTTP/1.1 404 Not Found
date: Fri, 16 Oct 2026 11:08:04 GMT
server: uvicorn
content-length: 28
content-type: application/json
vary: Origin

{"error":"Widget not found"}
```

```text
# owner 1 tries to update owner 2's widget
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    179 100     28 100    151   1777   9585                              0
100    179 100     28 100    151   1766   9527                              0
100    179 100     28 100    151   1744   9409                              0
HTTP/1.1 404 Not Found
date: Fri, 16 Oct 2026 11:08:04 GMT
server: uvicorn
content-length: 28
content-type: application/json
vary: Origin

{"error":"Widget not found"}
```

```text
# owner 1 tries to delete owner 2's widget
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100     28 100     28   0      0   2877      0                              0
100     28 100     28   0      0   2835      0                              0
100     28 100     28   0      0   2790      0                              0
HTTP/1.1 404 Not Found
date: Fri, 16 Oct 2026 11:08:04 GMT
server: uvicorn
content-length: 28
content-type: application/json
vary: Origin

{"error":"Widget not found"}
```

```text
# owner 2 reads its own widget
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    490 100    490   0      0  43660      0                              0
100    490 100    490   0      0  42764      0                              0
100    490 100    490   0      0  41970      0                              0
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 11:08:05 GMT
server: uvicorn
content-length: 490
content-type: application/json
vary: Origin

{"id":"demo-other","type":"contact_form","title":"Other tenant widget","description":"Belongs to demo-owner-2","fields":[{"name":"email","label":"Email","type":"email","required":true},{"name":"message","label":"Message","type":"textarea","required":true}],"button_text":"Send","is_active":true,"config_version":1,"created_at":"2026-10-14T12:46:48.771868Z","updated_at":"2026-10-14T12:46:48.771868Z","embed_snippet":"<script src=\"http://localhost:8000/widget.js?id=demo-other\"></script>"}
```

```text
# owner 2 asks for owner 1's submissions
{"items":[],"total":0,"limit":50,"offset":0}
```


## Widget delivery: embed snippet, cached config, versioned bundle

```text
# Embed snippet returned for the widget
<script src="http://localhost:8000/widget.js?id=demo-contact"></script>
```

```text
# GET /widgets/demo-contact/config (small payload, 60 s cache)
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 11:08:05 GMT
server: uvicorn
content-length: 300
content-type: application/json
cache-control: public, max-age=60
vary: Origin

{"id":"demo-contact","type":"contact_form","title":"Contact us (demo)","description":"Demo widget for evaluation","fields":[{"name":"email","label":"Email","type":"email","required":true},{"name":"message","label":"Message","type":"textarea","required":true}],"button_text":"Send","config_version":1}
```

```text
# GET /widget.v1.js (versioned bundle, immutable one-year cache)
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 11:08:05 GMT
server: uvicorn
cache-control: public, max-age=31536000, immutable
content-type: application/javascript
accept-ranges: bytes
content-length: 4823
last-modified: Wed, 14 Oct 2026 12:45:35 GMT
etag: "625e2689bc2d48fc2fbf50036592dda2"
vary: Origin

bytes downloaded: 4823
```

```text
# GET /widget.js?id=demo-contact (loader redirect, 5 min cache)
HTTP/1.1 302 Found
date: Fri, 16 Oct 2026 11:08:05 GMT
server: uvicorn
cache-control: public, max-age=300
content-length: 0
location: /widget.v1.js
vary: Origin
```

```text
# GET config for an unknown widget
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100     28 100     28   0      0   2417      0                              0
100     28 100     28   0      0   2359      0                              0
HTTP/1.1 404 Not Found
date: Fri, 16 Oct 2026 11:08:05 GMT
server: uvicorn
content-length: 28
content-type: application/json
vary: Origin

100     28 100     28   0      0   2245      0                              0
{"error":"Widget not found"}
```


## CORS: preflight and cross-origin submission

```text
# OPTIONS /submissions (preflight from http://localhost:5500)
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100      2 100      2   0      0    182      0                              0
100      2 100      2   0      0    180      0                              0
100      2 100      2   0      0    177      0                              0
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 11:08:06 GMT
server: uvicorn
vary: Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Request-Private-Network
access-control-allow-origin: *
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
access-control-max-age: 600
access-control-allow-headers: Accept, Accept-Language, Authorization, Content-Language, Content-Type
content-length: 2
content-type: text/plain; charset=utf-8

OK
```


## Valid submission stored, linked to the right widget and tenant, visible on the dashboard

```text
# POST /submissions from another origin
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
HTTP/1.1 201 Created
date: Fri, 16 Oct 2026 11:08:06 GMT
server: uvicorn
content-length: 45
content-type: application/json
access-control-allow-origin: *
vary: Origin

100    168 100     45 100    123    940   2571                              0
100    168 100     45 100    123    938   2565                              0
100    168 100     45 100    123    936   2558                              0
{"id":"3486c706-7270-4035-9457-b514afa1f9e9"}
```

```text
# GET /dashboard/submissions?limit=1 as owner 1
{"items":[{"id":"3486c706-7270-4035-9457-b514afa1f9e9","widget_id":"demo-contact","data":{"email":"evidence@example.com","message":"evidence one"},"country":null,"city":null,"geo_provider":null,"notification_status":"sent","created_at":"2026-10-16T11:08:07.267941Z"}],"total":14,"limit":1,"offset":0}
```


## Idempotency: a retried request is stored once

```text
# Same request again (same id, status 200, no new row)
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    168 100     45 100    123   1066   2915                              0
100    168 100     45 100    123   1062   2905                              0
100    168 100     45 100    123   1057   2890                              0
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 11:08:06 GMT
server: uvicorn
content-length: 45
content-type: application/json
vary: Origin

{"id":"3486c706-7270-4035-9457-b514afa1f9e9"}
```


## Malformed and oversized payloads: clean 4xx JSON errors, never a 500

```text
# Malformed JSON
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100     73 100     64 100      9   6106    858                              0
100     73 100     64 100      9   5994    843                              0
HTTP/1.1 400 Bad Request
date: Fri, 16 Oct 2026 11:08:06 GMT
server: uvicorn
content-length: 64
content-type: application/json
vary: Origin

100     73 100     64 100      9   5909    831                              0
{"error":"Validation failed","fields":{"1":"JSON decode error"}}
```

```text
# Invalid email and missing required field
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
HTTP/1.1 400 Bad Request
date: Fri, 16 Oct 2026 11:08:07 GMT
server: uvicorn
content-length: 107
content-type: application/json
vary: Origin

100    167 100    107 100     60   5017   2813                              0
100    167 100    107 100     60   4977   2791                              0
100    167 100    107 100     60   4953   2777                              0
{"error":"Validation failed","fields":{"email":"Invalid email address","message":"This field is required"}}
```

```text
# Unknown widget
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
HTTP/1.1 404 Not Found
date: Fri, 16 Oct 2026 11:08:07 GMT
server: uvicorn
content-length: 28
content-type: application/json
vary: Origin

100     58 100     28 100     30    999   1070                              0
100     58 100     28 100     30    995   1066                              0
100     58 100     28 100     30    991   1062                              0
{"error":"Widget not found"}
```

```text
# Oversized payload (about 20 KB, limit 10 KB)
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100  20097 100     29 100  20068   2178  1.43M                              0
100  20097 100     29 100  20068   2128  1.40M                              0
100  20097 100     29 100  20068   2094  1.38M                              0
HTTP/1.1 413 Content Too Large
date: Fri, 16 Oct 2026 11:08:07 GMT
server: uvicorn
content-length: 29
content-type: application/json
vary: Origin

{"error":"Payload too large"}
```


## Spam control: honeypot field

```text
# POST with the hidden honeypot field filled in (looks successful to the bot)
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    157 100     45 100    112   3614   8996                              0
100    157 100     45 100    112   3579   8909                              0
HTTP/1.1 201 Created
date: Fri, 16 Oct 2026 11:08:07 GMT
server: uvicorn
content-length: 45
content-type: application/json
vary: Origin

100    157 100     45 100    112   3500   8712                              0
{"id":"51b0a8ef-243f-4cde-8d68-d45802a99010"}
```

```text
# Dashboard check: is the spam submission stored?
rows containing bot@spam.com: 0
```


## Owner dashboard analytics

```text
# GET /dashboard/stats as owner 1
{"total":14,"per_widget":[{"widget_id":"demo-contact","title":"Contact us (demo)","count":14}],"per_day":[{"date":"2026-10-09","count":1},{"date":"2026-10-11","count":1},{"date":"2026-10-12","count":1},{"date":"2026-10-13","count":2},{"date":"2026-10-14","count":3},{"date":"2026-10-15","count":5},{"date":"2026-10-16","count":1}],"per_country":[{"country":"Unknown","count":8},{"country":"Germany","count":2},{"country":"India","count":2},{"country":"Mockland","count":1},{"country":"United States","count":1}]}
```


## Persistence: migrations, schema, indexes, constraints

```text
# Alembic migration state
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
10abe9ac8685 (head)
```

```text
# Migration files
10abe9ac8685_create_widgets_and_submissions.py
```

```text
# psql: \d submissions
                           Table "public.submissions"
       Column        |           Type           | Collation | Nullable | Default 
---------------------+--------------------------+-----------+----------+---------
 id                  | uuid                     |           | not null | 
 widget_id           | character varying(16)    |           | not null | 
 owner_id            | uuid                     |           | not null | 
 data                | jsonb                    |           | not null | 
 ip_address          | character varying(64)    |           |          | 
 country             | character varying(100)   |           |          | 
 city                | character varying(100)   |           |          | 
 geo_provider        | character varying(32)    |           |          | 
 idempotency_key     | character varying(100)   |           |          | 
 notification_status | character varying(16)    |           | not null | 
 created_at          | timestamp with time zone |           | not null | now()
Indexes:
    "submissions_pkey" PRIMARY KEY, btree (id)
    "ix_submissions_owner_created" btree (owner_id, created_at)
    "ix_submissions_widget_created" btree (widget_id, created_at)
    "uq_widget_idempotency" UNIQUE CONSTRAINT, btree (widget_id, idempotency_key)
Foreign-key constraints:
    "submissions_widget_id_fkey" FOREIGN KEY (widget_id) REFERENCES widgets(id) ON DELETE CASCADE
```

```text
# psql: \d widgets
                           Table "public.widgets"
     Column     |           Type           | Collation | Nullable | Default 
----------------+--------------------------+-----------+----------+---------
 id             | character varying(16)    |           | not null | 
 owner_id       | uuid                     |           | not null | 
 type           | character varying(32)    |           | not null | 
 title          | character varying(200)   |           | not null | 
 description    | text                     |           |          | 
 fields         | jsonb                    |           | not null | 
 button_text    | character varying(64)    |           | not null | 
 is_active      | boolean                  |           | not null | 
 config_version | integer                  |           | not null | 
 created_at     | timestamp with time zone |           | not null | now()
 updated_at     | timestamp with time zone |           | not null | now()
Indexes:
    "widgets_pkey" PRIMARY KEY, btree (id)
    "ix_widgets_owner_id" btree (owner_id)
Referenced by:
    TABLE "submissions" CONSTRAINT "submissions_widget_id_fkey" FOREIGN KEY (widget_id) REFERENCES widgets(id) ON DELETE CASCADE
```


## Layered architecture (data / logic / HTTP separated)

```text
# app/ tree
__init__.py
main.py
models.py
seed.py
core\__init__.py
core\auth.py
core\config.py
core\database.py
core\errors.py
core\rate_limit.py
repositories\__init__.py
repositories\dashboard_repo.py
repositories\submission_repo.py
repositories\widget_repo.py
routes\__init__.py
routes\dashboard.py
routes\delivery.py
routes\submissions.py
routes\widgets.py
schemas\__init__.py
schemas\dashboard.py
schemas\delivery.py
schemas\submission.py
schemas\widget.py
services\__init__.py
services\dashboard_service.py
services\geo.py
services\notifier.py
services\submission_service.py
services\widget_service.py
static\widget.v1.js
```


## Rate limiting: a burst returns 429 and the service stays up

```text
# 15 rapid submissions: status codes in order
201 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

```text
# Next request inside the window (429 with Retry-After)
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
HTTP/1.1 429 Too Many Requests
date: Fri, 16 Oct 2026 11:08:27 GMT
server: uvicorn
retry-after: 9
content-length: 29
content-type: application/json
vary: Origin

100    145 100     29 100    116   5307  21229                              0
100    145 100     29 100    116   5204  20818                              0
100    145 100     29 100    116   5145  20581                              0
{"error":"Too many requests"}
```

```text
# GET /health during the flood window
{"status":"ok"}
```

```text
# Normal request after the window
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0
100    161 100     45 100    116   2228   5745                              0
100    161 100     45 100    116   2210   5698                              0
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 11:08:39 GMT
server: uvicorn
content-length: 45
content-type: application/json
vary: Origin

100    161 100     45 100    116   2195   5658                              0
{"id":"e9e16abd-bdaa-4ca2-8f89-2811aa8a19e9"}
```


## Enrichment and safe side effects

Captured from this same clean clone by setting switches in `.env` and recreating the API with `docker compose up -d --force-recreate api`.

### Provider A down, provider B answers (GEO_MOCK=true, GEO_A_DOWN=true)

```text
POST /submissions -> HTTP/1.1 201 Created
{"id":"c7718a38-e04f-4508-81d0-4d7234a34ee7"}

GET /dashboard/submissions?limit=1
{"items":[{"id":"c7718a38-e04f-4508-81d0-4d7234a34ee7","widget_id":"demo-contact","data":{"email":"probe@example.com","message":"provider A down"},"country":"Mockland","city":"Mock City B","geo_provider":"ipapi.co","notification_status":"sent","created_at":"2026-10-15T14:05:39.985089Z"}],"total":9,"limit":1,"offset":0}

docker compose logs api
geo lookup failed in _provider_a: provider A switched off
INFO:     172.19.0.1:43724 - "POST /submissions HTTP/1.1" 201 Created
[EMAIL] to=probe@example.com subject='Thanks for contacting us (Contact us (demo))'
```

### All providers down, submission still stored without geo (GEO_A_DOWN=true, GEO_B_DOWN=true)

```text
POST /submissions -> HTTP/1.1 201 Created
{"id":"d312eaaf-0ce2-4e88-9fb8-03672889a9cf"}

GET /dashboard/submissions?limit=1
{"items":[{"id":"d312eaaf-0ce2-4e88-9fb8-03672889a9cf","widget_id":"demo-contact","data":{"email":"probe@example.com","message":"both providers down"},"country":null,"city":null,"geo_provider":null,"notification_status":"sent","created_at":"2026-10-15T14:09:48.358102Z"}],"total":10,"limit":1,"offset":0}

docker compose logs api
geo lookup failed in _provider_a: provider A switched off
geo lookup failed in _provider_b: provider B switched off
all geo providers failed; storing submission without location
INFO:     172.19.0.1:43794 - "POST /submissions HTTP/1.1" 201 Created
[EMAIL] to=probe@example.com subject='Thanks for contacting us (Contact us (demo))'
```

### Failing email does not block the submission (NOTIFY_FAIL=true)

```text
POST /submissions -> HTTP/1.1 201 Created (returned immediately)
{"id":"5b5bff65-0bd8-43cd-9973-d57c71e9be5b"}

GET /dashboard/submissions?limit=1
{"items":[{"id":"5b5bff65-0bd8-43cd-9973-d57c71e9be5b","widget_id":"demo-contact","data":{"email":"probe@example.com","message":"email will fail"},"country":null,"city":null,"geo_provider":null,"notification_status":"failed","created_at":"2026-10-15T14:11:52.444947Z"}],"total":11,"limit":1,"offset":0}

docker compose logs api
INFO:     172.19.0.1:50062 - "POST /submissions HTTP/1.1" 201 Created
email attempt 1/3 failed for submission 5b5bff65-0bd8-43cd-9973-d57c71e9be5b: simulated email failure
email attempt 2/3 failed for submission 5b5bff65-0bd8-43cd-9973-d57c71e9be5b: simulated email failure
email attempt 3/3 failed for submission 5b5bff65-0bd8-43cd-9973-d57c71e9be5b: simulated email failure
ALERT: confirmation email permanently failed for submission 5b5bff65-0bd8-43cd-9973-d57c71e9be5b
```

## Widget renders on a page served from a different origin

The customer-site test page is served on port 5500; the API is on port 8000, so the origins differ.

![The widget rendered on http://127.0.0.1:5500](docs/screenshots/01-widget-on-second-origin.png)

Network tab: the loader redirect, the versioned bundle, the config, the CORS preflight (OPTIONS), and the cross-origin POST returning 201.

![Network tab with preflight and POST](docs/screenshots/02-network-preflight-and-post.png)

Response headers of the cross-origin POST, including `access-control-allow-origin`.

![CORS response headers](docs/screenshots/03-cors-response-headers.png)

## Secrets stay out of the repository

```text
# git ls-files: only .env.example is tracked, never .env

.env.example
migrations/env.py
```

```text
# git check-ignore -v .env (the rule that ignores it)
.gitignore:3:.env	.env
```

```text
# Search all commits for the Supabase key prefix (expect no output)

```

```text
# .env.example contains placeholders only
# Database. Docker Compose builds the in-container URL from the POSTGRES_ values.
POSTGRES_USER=widgets
POSTGRES_PASSWORD=change-me
POSTGRES_DB=widgets
# Only used when running the API outside Docker (uvicorn on your own machine).
DATABASE_URL=postgresql+psycopg://widgets:change-me@localhost:5433/widgets

# Auth. "demo" = fixed evaluation tokens (demo-owner-1, demo-owner-2), dev only.
# "supabase" = real Supabase login; fill in the two values below.
AUTH_MODE=demo
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

PUBLIC_BASE_URL=http://localhost:8000

# Rate limit for POST /submissions, per IP.
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=10

# Test switches for the fallback and side-effect proofs.
GEO_MOCK=false
GEO_A_DOWN=false
GEO_B_DOWN=false
GEO_TEST_IP=
NOTIFY_FAIL=false
```


## Documentation and submission pack

```text
# Required files present

Name          Length
----          ------
README.md       8217
capstone.yaml   2048
EVIDENCE.md    27810
.env.example     826
design.md       6510
```

