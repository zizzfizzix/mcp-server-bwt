import re
import warnings
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from types import TracebackType
from typing import Any, Self

from bing_webmaster_tools import BingWebmasterClient, Settings, utils
from bing_webmaster_tools.models import base as models_base
from bing_webmaster_tools.services import (
    content_blocking,
    content_management,
    crawling,
    keyword_analysis,
    link_analysis,
    regional_settings,
    site_management,
    submission,
    traffic_analysis,
    url_management,
)
from pydantic import SecretStr

# .NET JSON date: milliseconds since the Unix epoch (always UTC), optional offset suffix
_NET_DATE = re.compile(r"/Date\((-?\d+)(?:[+-]\d{4})?\)/")
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def parse_timestamp_utc(value: Any) -> datetime:
    """Parse an API date into a UTC-aware datetime.

    Upstream returns a naive datetime in the server's local time, which serializes
    without an offset and fails MCP clients' RFC 3339 ``date-time`` check (#6).
    ``/Date(ms)/`` values are decoded here so the result doesn't depend on how
    upstream interprets them. RFC 3339 date-times, which is how the models serialize
    dates, are accepted too, so a dumped row validates again (mcp re-validates
    paged results, #39). Anything else still goes through upstream's parser.
    """
    if isinstance(value, str) and (match := _NET_DATE.search(value)):
        return _EPOCH + timedelta(milliseconds=int(match.group(1)))
    if isinstance(value, str) and "T" in value:
        try:
            iso = datetime.fromisoformat(value)
        except ValueError:
            pass
        else:
            # Only values with an explicit offset: a naive one has no known zone
            if iso.tzinfo is not None:
                return iso.astimezone(UTC)
    parsed = utils.parse_timestamp_from_api(value)
    # Upstream's parser yields local time when it doesn't attach a timezone
    return parsed.astimezone(UTC)


# Every upstream model date field is parsed through this name in the base model
if hasattr(models_base, "parse_timestamp_from_api"):
    models_base.parse_timestamp_from_api = parse_timestamp_utc
else:
    warnings.warn(
        "bing_webmaster_tools.models.base no longer uses parse_timestamp_from_api; "
        "API dates may be returned without a UTC offset (#6)",
        stacklevel=1,
    )


@dataclass
class SiteInfo:
    site_url: str
    last_crawl_date: str | None = None
    crawl_allowed: bool = True
    sitemaps: list[str] = field(default_factory=list)


class BingWebmasterService:
    def __init__(self, api_key: str) -> None:
        self.settings = Settings(
            api_key=SecretStr(api_key),
            base_url="https://ssl.bing.com/webmaster/api.svc/json",
            timeout=30,
            max_retries=3,
            rate_limit_calls=5,
            rate_limit_period=1,
            disable_destructive_operations=False,
        )
        self.client: BingWebmasterClient | None = None

    async def __aenter__(self) -> Self:
        self.client = BingWebmasterClient(self.settings)
        await self.client.__aenter__()

        # Expose all services directly
        self.sites = site_management.SiteManagementService(self.client)
        self.submission = submission.SubmissionService(self.client)
        self.traffic = traffic_analysis.TrafficAnalysisService(self.client)
        self.crawling = crawling.CrawlingService(self.client)
        self.keywords = keyword_analysis.KeywordAnalysisService(self.client)
        self.links = link_analysis.LinkAnalysisService(self.client)
        self.content = content_management.ContentManagementService(self.client)
        self.blocking = content_blocking.ContentBlockingService(self.client)
        self.regional = regional_settings.RegionalSettingsService(self.client)
        self.urls = url_management.UrlManagementService(self.client)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
