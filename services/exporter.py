from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from config import RESULTS_DIR
from models import IPLookupResult
from ui.lookup_view import result_to_text
from utils.formatting import safe_filename


class Exporter:
    def __init__(self, directory: Path = RESULTS_DIR) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def export(self, result: IPLookupResult, kind: str) -> Path:
        kind = kind.lower()
        if kind == "json":
            return self.export_json(result)
        if kind == "txt":
            return self.export_txt(result)
        if kind == "csv":
            return self.export_csv(result)
        raise ValueError("Unsupported export format.")

    def _path(self, ip: str, suffix: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.directory / f"{safe_filename(ip)}_{timestamp}.{suffix}"

    def export_json(self, result: IPLookupResult) -> Path:
        path = self._path(result.ip, "json")
        path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
        return path

    def export_txt(self, result: IPLookupResult) -> Path:
        path = self._path(result.ip, "txt")
        path.write_text(result_to_text(result), encoding="utf-8")
        return path

    def export_csv(self, result: IPLookupResult) -> Path:
        path = self._path(result.ip, "csv")
        row = flatten_result(result)
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)
        return path


def flatten_result(result: IPLookupResult) -> dict[str, object]:
    data = result.to_dict()
    row: dict[str, object] = {
        "ip": data["ip"],
        "version": data["version"],
        "scope": data["scope"],
        "hostname": data["hostname"],
    }
    for section in ("network", "location", "rdap", "metadata"):
        for key, value in data[section].items():
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
                value = "; ".join(str(item) for item in value)
            row[f"{section}_{key}"] = value
    return row
