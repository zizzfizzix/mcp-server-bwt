from dataclasses import dataclass, field
from typing import List, Optional, Any
from pydantic import SecretStr
from bing_webmaster_tools import BingWebmasterClient, Settings
from bing_webmaster_tools.services import (
    site_management,
    submission,
    traffic_analysis,
    crawling,
    keyword_analysis,
    link_analysis,
    content_management,
    content_blocking,
    regional_settings,
    url_management,
)


@dataclass
class SiteInfo:
    site_url: str
    last_crawl_date: Optional[str] = None
    crawl_allowed: bool = True
    sitemaps: List[str] = field(default_factory=list)


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
        self.client: Optional[BingWebmasterClient] = None

    async def __aenter__(self) -> "BingWebmasterService":
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
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
