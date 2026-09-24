import asyncio
import time
from datetime import UTC, datetime, timedelta, timezone

import pytest
from bing_webmaster_tools import utils
from bing_webmaster_tools.models.traffic_analysis import QueryStats

from mcp_server_bwt.services.bing_webmaster import (
    BingWebmasterService,
    parse_timestamp_utc,
)


def test_service_context_manager_returns_self_and_propagates_errors() -> None:
    """Regression for #9: the typed __aenter__/__aexit__ keep their runtime behavior."""
    service = BingWebmasterService("dummy")

    async def run() -> None:
        async with service as entered:
            assert entered is service
            assert entered.client is not None
            assert entered.sites is not None
            raise KeyError("boom")

    with pytest.raises(KeyError):
        asyncio.run(run())


def _query_stats(date: str) -> dict[str, object]:
    return {
        "__type": "QueryStats:#Microsoft.Bing.Webmaster.Api",
        "Date": date,
        "Query": "example",
        "AvgClickPosition": 1,
        "AvgImpressionPosition": 1,
        "Clicks": 1,
        "Impressions": 1,
    }


@pytest.mark.parametrize("tz", ["UTC", "America/New_York", "Asia/Tokyo"])
@pytest.mark.parametrize(
    "date", ["/Date(1781222400000)/", "/Date(1781222400000+0200)/"]
)
def test_api_dates_serialize_as_utc_rfc3339(
    monkeypatch: pytest.MonkeyPatch, tz: str, date: str
) -> None:
    """Regression for #6: dates carry a UTC offset and don't depend on the server timezone."""
    monkeypatch.setenv("TZ", tz)
    time.tzset()
    try:
        stats = QueryStats.model_validate(_query_stats(date))
    finally:
        monkeypatch.delenv("TZ")
        time.tzset()

    assert stats.model_dump(mode="json")["date"] == "2026-06-12T00:00:00Z"


@pytest.mark.parametrize(
    "upstream_result",
    [
        datetime(2026, 6, 12, tzinfo=UTC),  # upstream fixed: aware UTC
        datetime(2026, 6, 12, 2, tzinfo=timezone(timedelta(hours=2))),  # aware, offset
        datetime(2026, 6, 12),  # noqa: DTZ001  (upstream "fixed" to naive UTC)
    ],
)
def test_api_dates_independent_of_upstream_parser(
    monkeypatch: pytest.MonkeyPatch, upstream_result: datetime
) -> None:
    """#6: the fix keeps working whatever upstream's parser returns for /Date(ms)/."""
    monkeypatch.setattr(
        utils, "parse_timestamp_from_api", lambda _value: upstream_result
    )

    stats = QueryStats.model_validate(_query_stats("/Date(1781222400000)/"))

    assert stats.model_dump(mode="json")["date"] == "2026-06-12T00:00:00Z"


def test_unparseable_api_date_still_raises() -> None:
    """#6: non-/Date(ms)/ input keeps upstream's error instead of a silent default."""
    with pytest.raises(ValueError, match="Unable to parse date"):
        parse_timestamp_utc("2026-06-12")
