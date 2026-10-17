# BUILDLOG: AI usage

## How I used AI

I used Claude (claude.ai chat) as a step-by-step mentor while building this capstone on Windows with PowerShell, VS Code, and Docker Desktop. The AI proposed designs and wrote code blocks and commands. I ran every command myself, pasted the real output back, and only moved on once a stage worked. Every stage is a separate commit.

## Where AI helped

- Drafted the one-page design doc: data model, API contracts for the three request paths, and the layer structure (routes, services, repositories).
- Wrote the first versions of: widget CRUD with tenant isolation, the public submission endpoint (CORS, validation, 10 KB size limit, idempotency key, honeypot), the geo fallback chain, the background email job with retries, the cached delivery endpoints and widget script, the dashboard queries, the Dockerfile and Compose setup, the demo auth mode, and the seed script.
- Suggested the test approach for each probe: mock switches for the geo providers, an environment switch to force the email to fail, and a burst script for rate limiting.

## Where AI was wrong, or things went wrong, and what we changed

1. **My first tenant-isolation test proved nothing.** The instructions assumed a second Supabase user existed. I logged in as the same user twice, so "user 2" could read, update, and delete user 1's widget (200 and 204 instead of 404). I noticed from the output, created a genuinely different second user, and reran it: three 404s and an empty list.
2. **Auth kept returning 401 because my `.env` had `SUPABASE_URL` ending in `/rest/v1/`.** I copied the wrong URL from the dashboard. A direct request to Supabase worked, which showed the app's setting was the problem. Fixed by using the bare project URL.
3. **A command block was never run, so `app/routes/submissions.py` did not exist.** The server crashed with an ImportError. A directory listing showed the missing file and I recreated it.
4. **Logging in to Supabase with `curl.exe` failed** (empty response, then `unsupported_grant_type`). I switched to PowerShell's `Invoke-RestMethod`, which worked.
5. **Rate limiter design changed.** The AI first added `slowapi`, then explained that its decorator runs after request-body validation, so garbage payloads would never be counted. We wrote a small in-memory limiter as a FastAPI dependency instead, which counts every request. During the first burst test the server hung once; restarting uvicorn fixed it and I never identified the exact cause (probably a stuck `--reload`).
6. **The design doc said the honeypot returns 200; the code returns 201**, so a bot cannot tell it was caught. I updated the doc to match.
7. **`requirements.txt` was unpinned.** We pinned it with `pip freeze` so a stranger gets the versions I tested.
8. **The first evidence capture was useless.** `Start-Transcript` dropped the HTTP status lines and headers from `curl.exe`. We replaced it with a script that writes each command and its output into `EVIDENCE.md`.
9. **Test pages and servers:** `localhost:5500` was unreachable until I bound the test server to `127.0.0.1`, and running several test servers at once on the same port gave confusing results, so I ran one at a time.
10. **GitHub rejected pushes with an "Internal Server Error"** for a while; my commits stayed local until it recovered. This was GitHub's side, not the code.

## What I decided or changed myself

I chose the capstone because I wanted to understand how the application worked rather than just follow commands. I kept the scope focused on the required features and skipped the stretch goals so I could get the main functionality working and test it properly. I asked for explanations before running commands, which helped me understand what each step was doing. While debugging, I paid attention to which terminal was running the server, investigated the hanging server issue, and created a separate user to test whether one user could access another user's widgets. I also reviewed the project history and made changes to the code or documentation where necessary.

## What I can explain without help

I understand that a browser sends an OPTIONS preflight request before certain cross-origin requests, such as requests using JSON content types or custom headers, to check whether the origin, method, and headers are allowed. If the server does not respond correctly, the browser blocks the actual POST request. When a user tries to access another tenant's widget, the authentication token provides the owner_id, and the database query checks both the widget ID and the owner ID. If no matching row exists, the service raises a not-found error, and the handler returns a 404 instead of a 403 because the resource is not found within that user's accessible resources. For location and email failures, the geo lookup falls back to saving the record without location if its providers fail. The database record is committed before the email job starts, and the email runs in the background after the response is sent. Therefore, the visitor can still receive a 201 Created response, while an email failure updates notification_status and records a log alert.

