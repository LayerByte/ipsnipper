from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from time import perf_counter, time

from models import IPLookupResult, LocationInfo, LookupMetadata, NetworkInfo, RDAPInfo
from providers.base import ProviderError
from providers.ipwhois_provider import IPWhoIsProvider
from providers.rdap_provider import RDAPProvider
from services.reverse_dns import reverse_dns
from storage.settings import Settings
from utils.validators import classify_ip


class IPLookupService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ip_provider = IPWhoIsProvider(settings.request_timeout)
        self.rdap_provider = RDAPProvider(settings.request_timeout)
        self._cache: dict[str, tuple[float, IPLookupResult]] = {}

    def lookup(self, ip: str, force_refresh: bool = False) -> IPLookupResult:
        started = perf_counter()
        classification = classify_ip(ip)

        if not force_refresh:
            cached = self._cache.get(classification.ip)
            if cached and time() - cached[0] <= self.settings.cache_ttl_seconds:
                result = deepcopy(cached[1])
                result.metadata.cache_hit = True
                result.metadata.duration_seconds = perf_counter() - started
                return result

        result = IPLookupResult(
            ip=classification.ip,
            version=classification.version,
            scope=classification.scope,
            classification=classification,
        )

        if not classification.public_lookup_allowed:
            result.metadata.warnings.append(
                f"{classification.ip} belongs to a {classification.scope.lower()} address range. "
                "Public ISP and geographic information is not available for this address."
            )
            result.metadata.duration_seconds = perf_counter() - started
            return result

        with ThreadPoolExecutor(max_workers=3) as executor:
            provider_future = executor.submit(self._provider_lookup, classification.ip)
            dns_future = executor.submit(reverse_dns, classification.ip) if self.settings.reverse_dns else None
            rdap_future = executor.submit(self._rdap_lookup, classification.ip) if self.settings.rdap else None

            location, network, provider_warning = provider_future.result()
            result.location = location
            result.network = network
            result.metadata.source = self.ip_provider.name
            if provider_warning:
                result.metadata.warnings.append(provider_warning)

            if dns_future:
                hostname, dns_warning = dns_future.result()
                result.network.hostname = hostname
                result.metadata.reverse_dns_source = "System DNS Resolver"
                if dns_warning:
                    result.metadata.warnings.append(dns_warning)

            if rdap_future:
                rdap, rdap_warning = rdap_future.result()
                result.rdap = rdap
                result.metadata.rdap_source = self.rdap_provider.name
                if rdap_warning:
                    result.metadata.warnings.append(rdap_warning)
                result.network.cidr = result.network.cidr or rdap.cidr
                result.network.registry = result.network.registry or rdap.registry

        result.metadata.duration_seconds = perf_counter() - started
        if not result.metadata.warnings:
            self._cache[classification.ip] = (time(), deepcopy(result))
        return result

    def _provider_lookup(self, ip: str) -> tuple[LocationInfo, NetworkInfo, str | None]:
        try:
            location, network = self.ip_provider.lookup(ip)
            return location, network, None
        except ProviderError as exc:
            return LocationInfo(), NetworkInfo(), str(exc)

    def _rdap_lookup(self, ip: str) -> tuple[RDAPInfo, str | None]:
        try:
            return self.rdap_provider.lookup(ip), None
        except ProviderError as exc:
            rdap = RDAPInfo(error=str(exc))
            return rdap, str(exc)
