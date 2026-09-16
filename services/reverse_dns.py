from __future__ import annotations

import socket


def reverse_dns(ip: str) -> tuple[str | None, str | None]:
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname, None
    except (socket.herror, socket.gaierror, TimeoutError, OSError):
        return None, "Reverse DNS record not found."
