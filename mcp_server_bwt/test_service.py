import asyncio
import time
from collections.abc import Callable, Iterator
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


@pytest.fixture
def set_tz(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[[str], None]]:
    """Switch the process timezone, restoring it (env and C-level) afterwards."""

    def apply(tz: str) -> None:
        monkeypatch.setenv("TZ", tz)
        time.tzset()

    yield apply
    monkeypatch.undo()
    time.tzset()


@pytest.mark.parametrize("tz", ["UTC", "America/New_York", "Asia/Tokyo"])
@pytest.mark.parametrize(
    "date", ["/Date(1781222400000)/", "/Date(1781222400000+0200)/"]
)
def test_api_dates_serialize_as_utc_rfc3339(
    set_tz: Callable[[str], None], tz: str, date: str
) -> None:
    """Regression for #6: dates carry a UTC offset and don't depend on the server timezone."""
    set_tz(tz)

    stats = QueryStats.model_validate(_query_stats(date))

    assert stats.model_dump(mode="json")["date"] == "2026-06-12T00:00:00Z"


def test_net_dates_are_exact_and_cover_the_full_range() -> None:
    """#6: millisecond precision and .NET DateTime.MinValue/MaxValue decode exactly."""
    assert parse_timestamp_utc("/Date(253402300799999)/") == datetime(
        9999, 12, 31, 23, 59, 59, 999000, tzinfo=UTC
    )
    assert parse_timestamp_utc("/Date(-62135596800000)/") == datetime(
        1, 1, 1, tzinfo=UTC
    )


def test_net_dates_do_not_depend_on_upstream_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#6: /Date(ms)/ is decoded here, so an upstream fix (or regression) can't change it."""

    def upstream(_value: object) -> datetime:
        raise AssertionError("upstream parser must not be used for /Date(ms)/")

    monkeypatch.setattr(utils, "parse_timestamp_from_api", upstream)

    stats = QueryStats.model_validate(_query_stats("/Date(1781222400000)/"))

    assert stats.model_dump(mode="json")["date"] == "2026-06-12T00:00:00Z"


@pytest.mark.parametrize(
    "upstream_result",
    [
        datetime(2026, 6, 12, tzinfo=UTC),
        datetime(2026, 6, 12, 2, tzinfo=timezone(timedelta(hours=2))),
        datetime(2026, 6, 12, 9),  # noqa: DTZ001  (naive local time, as upstream does today)
    ],
)
def test_other_formats_fall_back_to_upstream_as_utc(
    monkeypatch: pytest.MonkeyPatch,
    set_tz: Callable[[str], None],
    upstream_result: datetime,
) -> None:
    """#6: a format only upstream understands still comes back UTC-aware."""
    set_tz("Asia/Tokyo")
    monkeypatch.setattr(
        utils, "parse_timestamp_from_api", lambda _value: upstream_result
    )

    assert parse_timestamp_utc("some-future-format") == datetime(
        2026, 6, 12, tzinfo=UTC
    )


def test_unparseable_api_date_still_raises() -> None:
    """#6: unknown input keeps upstream's error instead of a silent default."""
    with pytest.raises(ValueError, match="Unable to parse date"):
        parse_timestamp_utc("2026-06-12")


@pytest.mark.parametrize(
    "value",
    ["2026-06-12T00:00:00Z", "2026-06-12T02:00:00+02:00", "2026-06-12T00:00:00"],
)
def test_serialized_dates_validate_again(value: str) -> None:
    """#39: a dumped row's RFC 3339 date parses back to the same UTC instant."""
    stats = QueryStats.model_validate(_query_stats(value))

    assert stats.date == datetime(2026, 6, 12, tzinfo=UTC)
    assert stats.model_dump(mode="json")["date"] == "2026-06-12T00:00:00Z"


def test_round_trip_of_a_dumped_row() -> None:
    stats = QueryStats.model_validate(_query_stats("/Date(1781222400000)/"))

    dumped = stats.model_dump(mode="json", by_alias=True)

    assert QueryStats.model_validate(dumped) == stats
