from __future__ import annotations

from typing import Any


def format_value(value: Any) -> str:
    if value in (None, "", [], {}):
        return "N/A"
    if isinstance(value, bool):
        return "YES" if value else "NO"
    return str(value)


def safe_filename(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)
    return cleaned.strip("._") or "lookup"
