from tdsnmp.utils.snmp_strings import strip_non_printable, tostr
from tdsnmp.utils.compat import iso_8859_1

def test_utils_000_strip_non_printable_regular():
    assert strip_non_printable('hello there') == 'hello there'


def test_utils_001_strip_non_printable_contains_binary():
    assert strip_non_printable(iso_8859_1(chr(20)) + 'my thingo' + iso_8859_1(chr(155))) == (
        'my thingo (contains binary)'
    )


def test_utils_002_strip_non_printable_only_binary():
    assert strip_non_printable(iso_8859_1(chr(20)) + iso_8859_1(chr(155))) == (
        '(contains binary)'
    )


def test_utils_003_tostr_none():
    assert tostr(None) is None


def test_utils_004_tostr_string():
    assert tostr('hello there') == 'hello there'


def test_utils_005_tostr_integer():
    assert tostr(1234) == '1234'