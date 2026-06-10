import os
from unittest.mock import patch

import pytest

from core.config import Settings, _parse_origins


# ── _parse_origins ────────────────────────────────────────────────────────────

def test_parse_origins_none_returns_localhost():
    assert _parse_origins(None) == ["http://localhost:3000"]


def test_parse_origins_empty_returns_localhost():
    assert _parse_origins("") == ["http://localhost:3000"]


def test_parse_origins_single_value():
    result = _parse_origins("https://example.com")
    assert result == ["https://example.com"]


def test_parse_origins_comma_separated():
    result = _parse_origins("https://a.com,https://b.com")
    assert result == ["https://a.com", "https://b.com"]


def test_parse_origins_strips_whitespace():
    result = _parse_origins("  https://a.com , https://b.com  ")
    assert result == ["https://a.com", "https://b.com"]


def test_parse_origins_skips_empty_segments():
    result = _parse_origins("https://a.com,,https://b.com")
    assert result == ["https://a.com", "https://b.com"]


# ── Settings ──────────────────────────────────────────────────────────────────

def test_settings_is_frozen():
    s = Settings()
    with pytest.raises(Exception):
        s.env = "production"


def test_settings_default_env_is_dev():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("HIGHFIVE_ENV", None)
        s = Settings()
    assert s.env == "dev"


def test_settings_cors_origins_from_env():
    with patch.dict(os.environ, {"HIGHFIVE_CORS_ORIGINS": "https://app.com"}):
        s = Settings()
    assert s.cors_origins == ["https://app.com"]


def test_settings_cors_origins_default_includes_localhost():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("HIGHFIVE_CORS_ORIGINS", None)
        s = Settings()
    assert any("localhost" in o for o in s.cors_origins)
