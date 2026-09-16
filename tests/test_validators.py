import pytest

from utils.validators import InvalidIPAddress, classify_ip, parse_ip


def test_ipv4_validation():
    assert str(parse_ip("8.8.8.8")) == "8.8.8.8"


def test_ipv6_validation():
    assert str(parse_ip("2001:4860:4860::8888")) == "2001:4860:4860::8888"


def test_invalid_input():
    with pytest.raises(InvalidIPAddress):
        parse_ip("bad-ip")


def test_private_classification():
    result = classify_ip("192.168.1.1")
    assert result.scope == "Private"
    assert result.public_lookup_allowed is False


def test_loopback_classification():
    result = classify_ip("127.0.0.1")
    assert result.scope == "Loopback"


def test_public_classification():
    result = classify_ip("8.8.8.8")
    assert result.scope == "Public"
    assert result.public_lookup_allowed is True
