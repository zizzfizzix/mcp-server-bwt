from dataclasses import dataclass
from typing import List, Optional
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
    url_management
)

@dataclass
class SiteInfo:
    site_url: str
    last_crawl_date: Optional[str] = None
    crawl_allowed: bool = True
    sitemaps: List[str] = None

class BingWebmasterService:
    def __init__(self, api_key: str):
        self.settings = Settings(api_key=api_key)
        self.client = None
        
    async def __aenter__(self):
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
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
