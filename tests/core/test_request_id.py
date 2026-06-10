import logging

import pytest

from core.request_id import (
    RequestIdLogFilter,
    _MAX_INBOUND_LENGTH,
    _coerce_inbound,
)


# ── _coerce_inbound ───────────────────────────────────────────────────────────

def test_coerce_none_returns_none():
    assert _coerce_inbound(None) is None


def test_coerce_empty_string_returns_none():
    assert _coerce_inbound("") is None


def test_coerce_whitespace_only_returns_none():
    assert _coerce_inbound("   ") is None


def test_coerce_control_char_returns_none():
    assert _coerce_inbound("abc\x01def") is None


def test_coerce_valid_id_returned_as_is():
    assert _coerce_inbound("my-request-id") == "my-request-id"


def test_coerce_strips_surrounding_whitespace():
    assert _coerce_inbound("  abc  ") == "abc"


def test_coerce_exact_max_length_accepted():
    val = "a" * _MAX_INBOUND_LENGTH
    assert _coerce_inbound(val) == val


def test_coerce_over_max_length_returns_none():
    val = "a" * (_MAX_INBOUND_LENGTH + 1)
    assert _coerce_inbound(val) is None


def test_coerce_printable_ascii_accepted():
    assert _coerce_inbound("abc-123_XYZ") == "abc-123_XYZ"


# ── RequestIdLogFilter ────────────────────────────────────────────────────────

def test_log_filter_adds_dash_when_no_request_context():
    f = RequestIdLogFilter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello", args=(), exc_info=None,
    )
    f.filter(record)
    assert record.request_id == "-"


def test_log_filter_returns_true():
    f = RequestIdLogFilter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello", args=(), exc_info=None,
    )
    assert f.filter(record) is True


def test_log_filter_sets_request_id_attribute():
    f = RequestIdLogFilter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello", args=(), exc_info=None,
    )
    f.filter(record)
    assert hasattr(record, "request_id")
