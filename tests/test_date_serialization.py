from datetime import datetime, timezone

from bing_webmaster_tools import utils
from bing_webmaster_tools.models.traffic_analysis import (
    QueryStats,
    RankAndTrafficStats,
)
from jsonschema import FormatChecker, validate

import mcp_server_bwt  # noqa: F401 - Must be imported to apply UTC date parsing patch
from mcp_server_bwt.tools.bing_webmaster import sanitize_dates


def test_parse_timestamp_from_api_utc():
    timestamp_str = "/Date(1741219200000)/"
    dt = utils.parse_timestamp_from_api(timestamp_str)
    assert dt.tzinfo == timezone.utc
    assert dt.year == 2025


def test_query_stats_date_serialization_iso_z():
    raw_item = {
        "__type": "QueryStats",
        "AvgClickPosition": 3,
        "AvgImpressionPosition": 5,
        "Clicks": 42,
        "Date": "/Date(1741219200000)/",
        "Impressions": 500,
        "Query": "mcp server bing webmaster",
    }
    qs = QueryStats.model_validate(raw_item)
    assert qs.date.tzinfo == timezone.utc

    dumped = qs.model_dump(mode="json", by_alias=True)
    assert "Date" in dumped
    assert dumped["Date"].endswith("Z") or "+00:00" in dumped["Date"]

    # Validate against strict JSON Schema date-time format (RFC 3339)
    schema = {"type": "string", "format": "date-time"}
    validate(instance=dumped["Date"], schema=schema, format_checker=FormatChecker())


def test_rank_and_traffic_stats_date_serialization():
    raw_item = {
        "__type": "RankAndTrafficStats",
        "Clicks": 100,
        "Date": "/Date(1741219200000)/",
        "Impressions": 2000,
    }
    stats = RankAndTrafficStats.model_validate(raw_item)
    assert stats.date.tzinfo == timezone.utc

    dumped = stats.model_dump(mode="json", by_alias=True)
    schema = {"type": "string", "format": "date-time"}
    validate(instance=dumped["Date"], schema=schema, format_checker=FormatChecker())


def test_sanitize_dates_helper():
    naive_dt = datetime(2026, 3, 5, 12, 0, 0)  # noqa: DTZ001
    aware_dt = sanitize_dates(naive_dt)
    assert aware_dt.tzinfo == timezone.utc

    raw_item = {
        "__type": "QueryStats",
        "AvgClickPosition": 1,
        "AvgImpressionPosition": 2,
        "Clicks": 10,
        "Date": "/Date(1741219200000)/",
        "Impressions": 100,
        "Query": "test",
    }
    qs = QueryStats.model_validate(raw_item)
    # Manually set naive date to test sanitize_dates fallback
    qs.date = naive_dt
    sanitized = sanitize_dates([qs])
    assert sanitized[0].date.tzinfo == timezone.utc
