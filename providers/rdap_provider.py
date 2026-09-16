from __future__ import annotations

from typing import Any

import requests

from models import RDAPInfo
from providers.base import Provider, ProviderError


class RDAPProvider(Provider):
    name = "RDAP / Regional Registry"

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    def lookup(self, ip: str) -> RDAPInfo:
        try:
            response = requests.get(f"https://rdap.org/ip/{ip}", timeout=self.timeout)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        except requests.Timeout as exc:
            raise ProviderError("RDAP lookup timed out.") from exc
        except requests.RequestException as exc:
            raise ProviderError("RDAP lookup failed.") from exc
        except ValueError as exc:
            raise ProviderError("RDAP returned invalid JSON.") from exc

        registration_date, last_updated = self._events(data.get("events") or [])
        return RDAPInfo(
            network_name=data.get("name"),
            handle=data.get("handle"),
            cidr=self._cidr(data),
            start_address=data.get("startAddress"),
            end_address=data.get("endAddress"),
            country=data.get("country"),
            registry=self._registry(data),
            registration_date=registration_date,
            last_updated=last_updated,
        )

    @staticmethod
    def _events(events: list[dict[str, Any]]) -> tuple[str | None, str | None]:
        registration_date = None
        last_updated = None
        for event in events:
            action = str(event.get("eventAction") or "").lower()
            if "registration" in action:
                registration_date = event.get("eventDate")
            if "last changed" in action or "last update" in action:
                last_updated = event.get("eventDate")
        return registration_date, last_updated

    @staticmethod
    def _cidr(data: dict[str, Any]) -> str | None:
        cidrs = data.get("cidr0_cidrs")
        if isinstance(cidrs, list) and cidrs:
            first = cidrs[0]
            prefix = first.get("v4prefix") or first.get("v6prefix")
            length = first.get("length")
            if prefix and length is not None:
                return f"{prefix}/{length}"
        return None

    @staticmethod
    def _registry(data: dict[str, Any]) -> str | None:
        port43 = data.get("port43")
        if isinstance(port43, str) and port43:
            return port43.split(".")[0].upper()
        return None
