from pathlib import Path

from models import IPClassification, IPLookupResult, LocationInfo, NetworkInfo
from services.exporter import Exporter
from storage.database import HistoryDatabase
from storage.settings import Settings


def sample_result():
    classification = IPClassification(
        ip="8.8.8.8",
        version=4,
        scope="Public",
        public_lookup_allowed=True,
        private=False,
        global_address=True,
        reserved=False,
        loopback=False,
        link_local=False,
        multicast=False,
        unspecified=False,
    )
    return IPLookupResult(
        ip="8.8.8.8",
        version=4,
        scope="Public",
        classification=classification,
        network=NetworkInfo(asn="AS15169", isp="Google LLC"),
        location=LocationInfo(country="United States", city="Mountain View"),
    )


def test_settings_corruption_falls_back(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("{bad json", encoding="utf-8")
    settings = Settings.load(path)
    assert settings.default_export == "json"


def test_history_database(tmp_path):
    db = HistoryDatabase(tmp_path / "history.db")
    db.add(sample_result())
    entries = db.list()
    assert entries[0].ip == "8.8.8.8"
    db.delete(entries[0].id)
    assert db.list() == []


def test_exporters(tmp_path):
    exporter = Exporter(Path(tmp_path))
    result = sample_result()
    assert exporter.export(result, "json").exists()
    assert exporter.export(result, "txt").exists()
    assert exporter.export(result, "csv").exists()
