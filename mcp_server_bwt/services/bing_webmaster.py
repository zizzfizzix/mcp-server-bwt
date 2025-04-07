from dataclasses import dataclass
from typing import List, Optional
from bing_webmaster_tools import BingWebmasterClient, Settings

@dataclass
class SiteInfo:
    site_url: str
    last_crawl_date: Optional[str] = None
    crawl_allowed: bool = True
    sitemaps: List[str] = None

class BingWebmasterService:
    def __init__(self, api_key: str):
        settings = Settings(api_key=api_key)
        self.client = BingWebmasterClient(settings)
        
        # Expose all services directly
        self.sites = self.client.sites
        self.submission = self.client.submission
        self.traffic = self.client.traffic
        self.crawling = self.client.crawling
        self.keywords = self.client.keywords
        self.links = self.client.links
        self.content = self.client.content
        self.blocking = self.client.blocking
        self.regional = self.client.regional
        self.urls = self.client.urls
   