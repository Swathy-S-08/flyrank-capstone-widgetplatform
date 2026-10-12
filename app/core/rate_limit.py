import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.core.config import settings

_hits: dict[str, deque] = defaultdict(deque)


def rate_limit_submissions(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = settings.rate_limit_window_seconds
    hits = _hits[ip]

    while hits and now - hits[0] > window:
        hits.popleft()

    if len(hits) >= settings.rate_limit_max_requests:
        retry_after = max(1, int(window - (now - hits[0])) + 1)
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(retry_after)},
        )
    hits.append(now)
