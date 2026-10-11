import uuid

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer = HTTPBearer(auto_error=False)


def get_current_owner(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> uuid.UUID:
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        resp = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {creds.credentials}",
                "apikey": settings.supabase_anon_key,
            },
            timeout=5,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Auth provider unreachable")
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return uuid.UUID(resp.json()["id"])
