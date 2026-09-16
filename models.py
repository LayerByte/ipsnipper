from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class IPClassification:
    ip: str
    version: int
    scope: str
    public_lookup_allowed: bool
    private: bool
    global_address: bool
    reserved: bool
    loopback: bool
    link_local: bool
    multicast: bool
    unspecified: bool
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class NetworkInfo:
    asn: str | None = None
    isp: str | None = None
    organization: str | None = None
    asn_organization: str | None = None
    cidr: str | None = None
    registry: str | None = None
    hostname: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class LocationInfo:
    country: str | None = None
    country_code: str | None = None
    region: str | None = None
    city: str | None = None
    postal: str | None = None
    timezone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    accuracy: str = "approximate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RDAPInfo:
    network_name: str | None = None
    handle: str | None = None
    cidr: str | None = None
    start_address: str | None = None
    end_address: str | None = None
    country: str | None = None
    registry: str | None = None
    registration_date: str | None = None
    last_updated: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class LookupMetadata:
    source: str = "local"
    rdap_source: str | None = None
    reverse_dns_source: str | None = None
    duration_seconds: float = 0.0
    cache_hit: bool = False
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class IPLookupResult:
    ip: str
    version: int
    scope: str
    classification: IPClassification
    network: NetworkInfo = field(default_factory=NetworkInfo)
    location: LocationInfo = field(default_factory=LocationInfo)
    rdap: RDAPInfo = field(default_factory=RDAPInfo)
    metadata: LookupMetadata = field(default_factory=LookupMetadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ip": self.ip,
            "version": self.version,
            "scope": self.scope.lower(),
            "hostname": self.network.hostname,
            "network": self.network.to_dict(),
            "location": self.location.to_dict(),
            "rdap": self.rdap.to_dict(),
            "classification": self.classification.to_dict(),
            "metadata": self.metadata.to_dict(),
        }
