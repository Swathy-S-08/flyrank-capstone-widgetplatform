import ipaddress
import logging
from dataclasses import dataclass

import httpx

from app.core.config import settings

log = logging.getLogger("geo")
TIMEOUT_SECONDS = 2.0


@dataclass
class GeoResult:
    country: str | None
    city: str | None
    provider: str


class ProviderError(Exception):
    pass


def _clip(value: str | None) -> str | None:
    return (value or "")[:100] or None


def _is_public(ip: str | None) -> bool:
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


def _provider_a(ip: str) -> GeoResult:
    if settings.geo_a_down:
        raise ProviderError("provider A switched off")
    if settings.geo_mock:
        return GeoResult("Mockland", "Mock City A", "ip-api.com")
    resp = httpx.get(
        f"http://ip-api.com/json/{ip}",
        params={"fields": "status,country,city"},
        timeout=TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "success":
        raise ProviderError("provider A returned no result")
    return GeoResult(_clip(data.get("country")), _clip(data.get("city")), "ip-api.com")


def _provider_b(ip: str) -> GeoResult:
    if settings.geo_b_down:
        raise ProviderError("provider B switched off")
    if settings.geo_mock:
        return GeoResult("Mockland", "Mock City B", "ipapi.co")
    resp = httpx.get(
        f"https://ipapi.co/{ip}/json/",
        headers={"User-Agent": "widget-platform/1.0"},
        timeout=TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise ProviderError("provider B returned an error")
    return GeoResult(_clip(data.get("country_name")), _clip(data.get("city")), "ipapi.co")


PROVIDERS = [_provider_a, _provider_b]


def lookup(ip: str | None) -> GeoResult | None:
    """Try provider A, then B. Never raises: no location is acceptable."""
    if settings.geo_test_ip:
        ip = settings.geo_test_ip  # dev/test only
    if not settings.geo_mock and not _is_public(ip):
        return None  # loopback and private addresses have no location

    for provider in PROVIDERS:
        try:
            return provider(ip)
        except (ProviderError, httpx.HTTPError, ValueError) as exc:
            log.warning("geo lookup failed in %s: %s", provider.__name__, exc)
    log.warning("all geo providers failed; storing submission without location")
    return None
