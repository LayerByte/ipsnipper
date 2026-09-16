from __future__ import annotations

import requests

from providers.base import Provider, ProviderError


class PublicIPProvider(Provider):
    name = "api.ipify.org"

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    def lookup(self, value: str = "") -> str:
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.Timeout as exc:
            raise ProviderError("Public IP provider timed out.") from exc
        except requests.RequestException as exc:
            raise ProviderError("Public IP provider unavailable.") from exc
        except ValueError as exc:
            raise ProviderError("Public IP provider returned invalid JSON.") from exc
        ip = data.get("ip")
        if not ip:
            raise ProviderError("Public IP provider returned no IP address.")
        return str(ip)
