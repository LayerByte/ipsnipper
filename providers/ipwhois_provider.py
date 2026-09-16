from __future__ import annotations

from typing import Any

import requests

from models import LocationInfo, NetworkInfo
from providers.base import Provider, ProviderError


class IPWhoIsProvider(Provider):
    name = "ipwho.is"

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    def lookup(self, ip: str) -> tuple[LocationInfo, NetworkInfo]:
        try:
            response = requests.get(f"https://ipwho.is/{ip}", timeout=self.timeout)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        except requests.Timeout as exc:
            raise ProviderError("IP provider timed out.") from exc
        except requests.RequestException as exc:
            raise ProviderError("IP provider unavailable.") from exc
        except ValueError as exc:
            raise ProviderError("IP provider returned invalid JSON.") from exc

        if not data.get("success"):
            raise ProviderError(str(data.get("message") or "IP provider returned no result."))

        timezone = data.get("timezone") or {}
        connection = data.get("connection") or {}
        asn_value = connection.get("asn")
        location = LocationInfo(
            country=data.get("country"),
            country_code=data.get("country_code"),
            region=data.get("region"),
            city=data.get("city"),
            postal=data.get("postal"),
            timezone=timezone.get("id") if isinstance(timezone, dict) else None,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )
        network = NetworkInfo(
            isp=connection.get("isp"),
            organization=connection.get("org"),
            asn=f"AS{asn_value}" if asn_value else None,
            asn_organization=connection.get("org"),
            cidr=connection.get("route"),
            registry=data.get("rir"),
        )
        return location, network
