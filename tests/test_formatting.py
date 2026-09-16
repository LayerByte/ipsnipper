from utils.formatting import format_value, safe_filename


def test_format_value_missing():
    assert format_value(None) == "N/A"
    assert format_value("") == "N/A"
    assert format_value({}) == "N/A"


def test_format_value_bool():
    assert format_value(True) == "YES"
    assert format_value(False) == "NO"


def test_safe_filename():
    assert safe_filename("8.8.8.8") == "8.8.8.8"
    assert safe_filename("../bad:name") == "bad_name"
