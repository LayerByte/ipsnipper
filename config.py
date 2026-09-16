from __future__ import annotations

from pathlib import Path

APP_NAME = "IPSNIPPER"
VERSION = "1.0.0"
REPOSITORY = "https://github.com/LayerByte/ipsnipper"
AUTHOR = "LayerByte"
LICENSE = "MIT"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
DATABASE_PATH = DATA_DIR / "ipsnipper.db"

DEFAULT_SETTINGS = {
    "reverse_dns": True,
    "rdap": True,
    "save_history": True,
    "auto_export": False,
    "default_export": "json",
    "request_timeout": 8.0,
    "show_coordinates": True,
    "cache_ttl_seconds": 600,
}
