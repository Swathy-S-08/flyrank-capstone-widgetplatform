import uuid

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer = HTTPBearer(auto_error=False)

# Fixed tokens for evaluation only (AUTH_MODE=demo). Never enable in production.
DEMO_OWNERS = {
    "demo-owner-1": uuid.UUID("00000000-0000-4000-8000-000000000001"),
    "demo-owner-2": uuid.UUID("00000000-0000-4000-8000-000000000002"),
}


def _owner_from_supabase(token: str) -> uuid.UUID:
    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="Supabase auth is not configured")
    try:
        resp = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_anon_key,
            },
            timeout=5,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Auth provider unreachable")
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return uuid.UUID(resp.json()["id"])


def get_current_owner(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> uuid.UUID:
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if settings.auth_mode == "demo":
        owner = DEMO_OWNERS.get(creds.credentials)
        if owner is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return owner
    return _owner_from_supabase(creds.credentials)
