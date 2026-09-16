from __future__ import annotations

import ipaddress

from models import IPClassification


class InvalidIPAddress(ValueError):
    pass


def parse_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    try:
        return ipaddress.ip_address(value.strip())
    except ValueError as exc:
        raise InvalidIPAddress("Invalid IP address. Enter a valid IPv4 or IPv6 value.") from exc


def classify_ip(value: str) -> IPClassification:
    ip_obj = parse_ip(value)
    if ip_obj.is_loopback:
        scope, allowed, reason = "Loopback", False, "Loopback addresses are local to this device."
    elif ip_obj.is_private:
        scope, allowed, reason = "Private", False, "Private addresses are not publicly routable."
    elif ip_obj.is_link_local:
        scope, allowed, reason = "Link Local", False, "Link-local addresses only work on a local network segment."
    elif ip_obj.is_multicast:
        scope, allowed, reason = "Multicast", False, "Multicast addresses do not identify a public host."
    elif ip_obj.is_unspecified:
        scope, allowed, reason = "Unspecified", False, "Unspecified addresses cannot be geolocated."
    elif ip_obj.is_reserved and not ip_obj.is_global:
        scope, allowed, reason = "Reserved", False, "Reserved addresses are not suitable for public lookup."
    elif ip_obj.is_global:
        scope, allowed, reason = "Public", True, ""
    else:
        scope, allowed, reason = "Non-public", False, "This address is not globally routable."

    return IPClassification(
        ip=str(ip_obj),
        version=ip_obj.version,
        scope=scope,
        public_lookup_allowed=allowed,
        private=ip_obj.is_private,
        global_address=ip_obj.is_global,
        reserved=ip_obj.is_reserved,
        loopback=ip_obj.is_loopback,
        link_local=ip_obj.is_link_local,
        multicast=ip_obj.is_multicast,
        unspecified=ip_obj.is_unspecified,
        reason=reason,
    )
