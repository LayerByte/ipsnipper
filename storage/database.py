from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config import DATABASE_PATH
from models import IPLookupResult


@dataclass(slots=True)
class HistoryEntry:
    id: int
    ip: str
    timestamp: str
    country: str | None
    city: str | None
    isp: str | None
    organization: str | None
    asn: str | None
    hostname: str | None
    lookup_status: str


class HistoryDatabase:
    def __init__(self, path: Path = DATABASE_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS lookup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    country TEXT,
                    city TEXT,
                    isp TEXT,
                    organization TEXT,
                    asn TEXT,
                    hostname TEXT,
                    lookup_status TEXT NOT NULL
                )
                """
            )

    def add(self, result: IPLookupResult, status: str = "success") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO lookup_history
                (ip, timestamp, country, city, isp, organization, asn, hostname, lookup_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.ip,
                    datetime.now().isoformat(timespec="seconds"),
                    result.location.country,
                    result.location.city,
                    result.network.isp,
                    result.network.organization,
                    result.network.asn,
                    result.network.hostname,
                    status,
                ),
            )

    def list(self, limit: int = 25) -> list[HistoryEntry]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, ip, timestamp, country, city, isp, organization, asn, hostname, lookup_status "
                "FROM lookup_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [HistoryEntry(*row) for row in rows]

    def get(self, entry_id: int) -> HistoryEntry | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, ip, timestamp, country, city, isp, organization, asn, hostname, lookup_status "
                "FROM lookup_history WHERE id = ?",
                (entry_id,),
            ).fetchone()
        return HistoryEntry(*row) if row else None

    def delete(self, entry_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM lookup_history WHERE id = ?", (entry_id,))

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM lookup_history")
