from dataclasses import dataclass, field
from types import TracebackType
from typing import Self

from bing_webmaster_tools import BingWebmasterClient, Settings
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
