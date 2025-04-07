from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp_server_bwt.services.bing_webmaster import BingWebmasterService, SiteInfo

def add_bing_webmaster_tools(mcp: FastMCP, service: BingWebmasterService):
    # Site Management Tools
    @mcp.tool()
    async def list_verified_sites() -> List[SiteInfo]:
        """List all verified sites in Bing Webmaster Tools.
        
        Returns:
            List of SiteInfo objects containing site information
        """
        return await service.sites.get_sites()
    
    @mcp.tool()
    async def add_site(site_url: str) -> Dict[str, Any]:
        """Add a new site to Bing Webmaster Tools.
        
        Args:
            site_url: The URL of the site to add
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.sites.add_site(site_url)
    
    @mcp.tool()
    async def verify_site(site_url: str) -> Dict[str, Any]:
        """Verify a site in Bing Webmaster Tools.
        
        Args:
            site_url: The URL of the site to verify
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.sites.verify_site(site_url)
    
    @mcp.tool()
    async def remove_site(site_url: str) -> Dict[str, Any]:
        """Remove a site from Bing Webmaster Tools.
        
        Args:
            site_url: The URL of the site to remove
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.sites.remove_site(site_url)
    
    @mcp.tool()
    async def get_site_roles(site_url: str) -> Dict[str, Any]:
        """Get roles for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the site roles
        """
        return await service.sites.get_site_roles(site_url)
    
    @mcp.tool()
    async def add_site_roles(site_url: str, roles: List[str]) -> Dict[str, Any]:
        """Add roles to a site.
        
        Args:
            site_url: The URL of the site
            roles: List of roles to add
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.sites.add_site_roles(site_url, roles)
    
    @mcp.tool()
    async def remove_site_role(site_url: str, role: str) -> Dict[str, Any]:
        """Remove a role from a site.
        
        Args:
            site_url: The URL of the site
            role: The role to remove
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.sites.remove_site_role(site_url, role)
    
    @mcp.tool()
    async def get_site_moves(site_url: str) -> Dict[str, Any]:
        """Get site moves for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the site moves
        """
        return await service.sites.get_site_moves(site_url)
    
    @mcp.tool()
    async def submit_site_move(site_url: str, new_url: str) -> Dict[str, Any]:
        """Submit a site move.
        
        Args:
            site_url: The current URL of the site
            new_url: The new URL of the site
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.sites.submit_site_move(site_url, new_url)
    
    # Submission Tools
    @mcp.tool()
    async def submit_url_for_indexing(url: str) -> Dict[str, Any]:
        """Submit a URL to Bing for indexing.
        
        Args:
            url: The URL to submit for indexing
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.submission.submit_url(url)
    
    @mcp.tool()
    async def submit_urls_batch(urls: List[str]) -> Dict[str, Any]:
        """Submit multiple URLs to Bing for indexing.
        
        Args:
            urls: List of URLs to submit for indexing
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.submission.submit_url_batch(urls)
    
    @mcp.tool()
    async def submit_content(url: str, content: str) -> Dict[str, Any]:
        """Submit content for a URL.
        
        Args:
            url: The URL to submit content for
            content: The content to submit
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.submission.submit_content(url, content)
    
    @mcp.tool()
    async def submit_feed(site_url: str, feed_url: str) -> Dict[str, Any]:
        """Submit a feed for a site.
        
        Args:
            site_url: The URL of the site
            feed_url: The URL of the feed
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.submission.submit_feed(site_url, feed_url)
    
    @mcp.tool()
    async def get_feeds(site_url: str) -> Dict[str, Any]:
        """Get feeds for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the feeds
        """
        return await service.submission.get_feeds(site_url)
    
    @mcp.tool()
    async def get_feed_details(site_url: str, feed_url: str) -> Dict[str, Any]:
        """Get details for a feed.
        
        Args:
            site_url: The URL of the site
            feed_url: The URL of the feed
            
        Returns:
            Dict containing the feed details
        """
        return await service.submission.get_feed_details(site_url, feed_url)
    
    @mcp.tool()
    async def remove_feed(site_url: str, feed_url: str) -> Dict[str, Any]:
        """Remove a feed from a site.
        
        Args:
            site_url: The URL of the site
            feed_url: The URL of the feed
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.submission.remove_feed(site_url, feed_url)
    
    @mcp.tool()
    async def get_url_submission_quota(site_url: str) -> Dict[str, Any]:
        """Get URL submission quota for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the URL submission quota
        """
        return await service.submission.get_url_submission_quota(site_url)
    
    @mcp.tool()
    async def get_content_submission_quota(site_url: str) -> Dict[str, Any]:
        """Get content submission quota for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the content submission quota
        """
        return await service.submission.get_content_submission_quota(site_url)
    
    @mcp.tool()
    async def fetch_url(url: str) -> Dict[str, Any]:
        """Fetch a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Dict containing the fetch result
        """
        return await service.submission.fetch_url(url)
    
    @mcp.tool()
    async def get_fetched_urls(site_url: str) -> Dict[str, Any]:
        """Get fetched URLs for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the fetched URLs
        """
        return await service.submission.get_fetched_urls(site_url)
    
    @mcp.tool()
    async def get_fetched_url_details(site_url: str, url: str) -> Dict[str, Any]:
        """Get details for a fetched URL.
        
        Args:
            site_url: The URL of the site
            url: The URL to get details for
            
        Returns:
            Dict containing the fetched URL details
        """
        return await service.submission.get_fetched_url_details(site_url, url)
    
    # Traffic Analysis Tools
    @mcp.tool()
    async def get_query_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict containing the query stats
        """
        return await service.traffic.get_query_stats(site_url, start_date, end_date)
    
    @mcp.tool()
    async def get_query_traffic_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query traffic stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict containing the query traffic stats
        """
        return await service.traffic.get_query_traffic_stats(site_url, start_date, end_date)
    
    @mcp.tool()
    async def get_query_page_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query page stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict containing the query page stats
        """
        return await service.traffic.get_query_page_stats(site_url, start_date, end_date)
    
    @mcp.tool()
    async def get_query_page_detail_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query page detail stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict containing the query page detail stats
        """
        return await service.traffic.get_query_page_detail_stats(site_url, start_date, end_date)
    
    @mcp.tool()
    async def get_page_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get page stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict containing the page stats
        """
        return await service.traffic.get_page_stats(site_url, start_date, end_date)
    
    @mcp.tool()
    async def get_page_query_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get page query stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict containing the page query stats
        """
        return await service.traffic.get_page_query_stats(site_url, start_date, end_date)
    
    @mcp.tool()
    async def get_rank_and_traffic_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get rank and traffic stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict containing the rank and traffic stats
        """
        return await service.traffic.get_rank_and_traffic_stats(site_url, start_date, end_date)
    
    # Crawling Tools
    @mcp.tool()
    async def get_crawl_stats(site_url: str) -> Dict[str, Any]:
        """Get crawl stats for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the crawl stats
        """
        return await service.crawling.get_crawl_stats(site_url)
    
    @mcp.tool()
    async def get_crawl_settings(site_url: str) -> Dict[str, Any]:
        """Get crawl settings for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the crawl settings
        """
        return await service.crawling.get_crawl_settings(site_url)
    
    @mcp.tool()
    async def save_crawl_settings(site_url: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Save crawl settings for a site.
        
        Args:
            site_url: The URL of the site
            settings: The crawl settings to save
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.crawling.save_crawl_settings(site_url, settings)
    
    @mcp.tool()
    async def get_crawl_issues(site_url: str) -> Dict[str, Any]:
        """Get crawl issues for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the crawl issues
        """
        return await service.crawling.get_crawl_issues(site_url)
    
    # Keyword Analysis Tools
    @mcp.tool()
    async def get_keyword(site_url: str, keyword: str) -> Dict[str, Any]:
        """Get keyword data for a site.
        
        Args:
            site_url: The URL of the site
            keyword: The keyword to get data for
            
        Returns:
            Dict containing the keyword data
        """
        return await service.keywords.get_keyword(site_url, keyword)
    
    @mcp.tool()
    async def get_keyword_stats(site_url: str, keyword: str) -> Dict[str, Any]:
        """Get keyword stats for a site.
        
        Args:
            site_url: The URL of the site
            keyword: The keyword to get stats for
            
        Returns:
            Dict containing the keyword stats
        """
        return await service.keywords.get_keyword_stats(site_url, keyword)
    
    @mcp.tool()
    async def get_related_keywords(site_url: str, keyword: str) -> Dict[str, Any]:
        """Get related keywords for a site.
        
        Args:
            site_url: The URL of the site
            keyword: The keyword to get related keywords for
            
        Returns:
            Dict containing the related keywords
        """
        return await service.keywords.get_related_keywords(site_url, keyword)
    
    # Link Analysis Tools
    @mcp.tool()
    async def get_link_counts(site_url: str) -> Dict[str, Any]:
        """Get link counts for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the link counts
        """
        return await service.links.get_link_counts(site_url)
    
    @mcp.tool()
    async def get_url_links(site_url: str, url: str) -> Dict[str, Any]:
        """Get links for a URL.
        
        Args:
            site_url: The URL of the site
            url: The URL to get links for
            
        Returns:
            Dict containing the links
        """
        return await service.links.get_url_links(site_url, url)
    
    @mcp.tool()
    async def get_deep_link(site_url: str, url: str) -> Dict[str, Any]:
        """Get deep link for a URL.
        
        Args:
            site_url: The URL of the site
            url: The URL to get deep link for
            
        Returns:
            Dict containing the deep link
        """
        return await service.links.get_deep_link(site_url, url)
    
    @mcp.tool()
    async def get_deep_link_blocks(site_url: str) -> Dict[str, Any]:
        """Get deep link blocks for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the deep link blocks
        """
        return await service.links.get_deep_link_blocks(site_url)
    
    @mcp.tool()
    async def add_deep_link_block(site_url: str, url: str) -> Dict[str, Any]:
        """Add a deep link block for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to block
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.links.add_deep_link_block(site_url, url)
    
    @mcp.tool()
    async def remove_deep_link_block(site_url: str, url: str) -> Dict[str, Any]:
        """Remove a deep link block for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to unblock
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.links.remove_deep_link_block(site_url, url)
    
    @mcp.tool()
    async def update_deep_link(site_url: str, url: str, deep_link: str) -> Dict[str, Any]:
        """Update a deep link for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to update deep link for
            deep_link: The new deep link
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.links.update_deep_link(site_url, url, deep_link)
    
    @mcp.tool()
    async def get_deep_link_algo_urls(site_url: str) -> Dict[str, Any]:
        """Get deep link algorithm URLs for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the deep link algorithm URLs
        """
        return await service.links.get_deep_link_algo_urls(site_url)
    
    @mcp.tool()
    async def get_connected_pages(site_url: str) -> Dict[str, Any]:
        """Get connected pages for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the connected pages
        """
        return await service.links.get_connected_pages(site_url)
    
    @mcp.tool()
    async def add_connected_page(site_url: str, url: str) -> Dict[str, Any]:
        """Add a connected page for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to add as a connected page
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.links.add_connected_page(site_url, url)
    
    # Content Management Tools
    @mcp.tool()
    async def get_url_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get URL info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get info for
            
        Returns:
            Dict containing the URL info
        """
        return await service.content.get_url_info(site_url, url)
    
    @mcp.tool()
    async def get_url_traffic_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get URL traffic info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get traffic info for
            
        Returns:
            Dict containing the URL traffic info
        """
        return await service.content.get_url_traffic_info(site_url, url)
    
    @mcp.tool()
    async def get_children_url_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get children URL info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get children info for
            
        Returns:
            Dict containing the children URL info
        """
        return await service.content.get_children_url_info(site_url, url)
    
    @mcp.tool()
    async def get_children_url_traffic_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get children URL traffic info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get children traffic info for
            
        Returns:
            Dict containing the children URL traffic info
        """
        return await service.content.get_children_url_traffic_info(site_url, url)
    
    # Content Blocking Tools
    @mcp.tool()
    async def get_blocked_urls(site_url: str) -> Dict[str, Any]:
        """Get blocked URLs for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the blocked URLs
        """
        return await service.blocking.get_blocked_urls(site_url)
    
    @mcp.tool()
    async def add_blocked_url(site_url: str, url: str) -> Dict[str, Any]:
        """Add a blocked URL for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to block
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.blocking.add_blocked_url(site_url, url)
    
    @mcp.tool()
    async def remove_blocked_url(site_url: str, url: str) -> Dict[str, Any]:
        """Remove a blocked URL for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to unblock
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.blocking.remove_blocked_url(site_url, url)
    
    @mcp.tool()
    async def get_active_page_preview_blocks(site_url: str) -> Dict[str, Any]:
        """Get active page preview blocks for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the active page preview blocks
        """
        return await service.blocking.get_active_page_preview_blocks(site_url)
    
    @mcp.tool()
    async def add_page_preview_block(site_url: str, url: str) -> Dict[str, Any]:
        """Add a page preview block for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to block from page previews
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.blocking.add_page_preview_block(site_url, url)
    
    @mcp.tool()
    async def remove_page_preview_block(site_url: str, url: str) -> Dict[str, Any]:
        """Remove a page preview block for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to unblock from page previews
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.blocking.remove_page_preview_block(site_url, url)
    
    # Regional Settings Tools
    @mcp.tool()
    async def get_country_region_settings(site_url: str) -> Dict[str, Any]:
        """Get country region settings for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict containing the country region settings
        """
        return await service.regional.get_country_region_settings(site_url)
    
    @mcp.tool()
    async def add_country_region_settings(site_url: str, country: str, region: str) -> Dict[str, Any]:
        """Add country region settings for a site.
        
        Args:
            site_url: The URL of the site
            country: The country code
            region: The region code
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.regional.add_country_region_settings(site_url, country, region)
    
    @mcp.tool()
    async def remove_country_region_settings(site_url: str, country: str, region: str) -> Dict[str, Any]:
        """Remove country region settings for a site.
        
        Args:
            site_url: The URL of the site
            country: The country code
            region: The region code
            
        Returns:
            Dict containing the result of the operation
        """
        return await service.regional.remove_country_region_settings(site_url, country, region) 