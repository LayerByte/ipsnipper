import requests

from providers.base import ProviderError
from providers.ipwhois_provider import IPWhoIsProvider
from providers.rdap_provider import RDAPProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_ipwhois_provider_parses_missing_fields(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse({"success": True}))
    location, network = IPWhoIsProvider(timeout=1).lookup("8.8.8.8")
    assert location.country is None
    assert network.asn is None


def test_ipwhois_provider_timeout(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "get", raise_timeout)
    try:
        IPWhoIsProvider(timeout=1).lookup("8.8.8.8")
    except ProviderError as exc:
        assert "timed out" in str(exc)
    else:
        assert False


def test_rdap_failure(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "get", raise_timeout)
    try:
        RDAPProvider(timeout=1).lookup("8.8.8.8")
    except ProviderError as exc:
        assert "timed out" in str(exc)
    else:
        assert False
