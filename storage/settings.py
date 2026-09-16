from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from config import DEFAULT_SETTINGS, SETTINGS_PATH


@dataclass(slots=True)
class Settings:
    reverse_dns: bool = True
    rdap: bool = True
    save_history: bool = True
    auto_export: bool = False
    default_export: str = "json"
    request_timeout: float = 8.0
    show_coordinates: bool = True
    cache_ttl_seconds: int = 600

    @classmethod
    def load(cls, path: Path = SETTINGS_PATH) -> "Settings":
        try:
            if not path.exists():
                return cls()
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return cls()
            clean = DEFAULT_SETTINGS.copy()
            clean.update({key: value for key, value in data.items() if key in clean})
            clean["default_export"] = str(clean["default_export"]).lower()
            if clean["default_export"] not in {"json", "txt", "csv"}:
                clean["default_export"] = "json"
            clean["request_timeout"] = max(1.0, min(float(clean["request_timeout"]), 60.0))
            clean["cache_ttl_seconds"] = max(0, int(clean["cache_ttl_seconds"]))
            return cls(**clean)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return cls()

    def save(self, path: Path = SETTINGS_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
