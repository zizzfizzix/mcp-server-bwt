from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp_server_bwt.services.bing_webmaster import BingWebmasterService, SiteInfo

def add_bing_webmaster_tools(mcp: FastMCP, service: BingWebmasterService):
    # Site Management Tools
    @mcp.tool()
    async def list_verified_sites() -> List[SiteInfo]:
        """List all verified sites in Bing Webmaster Tools.
        
        Returns:
            List[SiteInfo]: List of verified sites with their information
            
        Raises:
            BingWebmasterError: If sites cannot be retrieved
        """
        async with service as s:
            return await s.sites.get_sites()
    
    @mcp.tool()
    async def add_site(site_url: str) -> Dict[str, Any]:
        """Add a new site to Bing Webmaster Tools.
        
        Args:
            site_url: The URL of the site to add
            
        Returns:
            Dict[str, Any]: Result of the operation containing site information
            
        Raises:
            BingWebmasterError: If site cannot be added
        """
        async with service as s:
            return await s.sites.add_site(site_url=site_url)
    
    @mcp.tool()
    async def verify_site(site_url: str) -> Dict[str, Any]:
        """Verify a site in Bing Webmaster Tools.
        
        Args:
            site_url: The URL of the site to verify
            
        Returns:
            Dict[str, Any]: Result of the verification operation
            
        Raises:
            BingWebmasterError: If site cannot be verified
        """
        async with service as s:
            return await s.sites.verify_site(site_url=site_url)
    
    @mcp.tool()
    async def remove_site(site_url: str) -> Dict[str, Any]:
        """Remove a site from Bing Webmaster Tools.
        
        Args:
            site_url: The URL of the site to remove
            
        Returns:
            Dict[str, Any]: Result of the removal operation
            
        Raises:
            BingWebmasterError: If site cannot be removed
        """
        async with service as s:
            return await s.sites.remove_site(site_url=site_url)
    
    @mcp.tool()
    async def get_site_roles(site_url: str) -> Dict[str, Any]:
        """Get roles for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Site roles information
            
        Raises:
            BingWebmasterError: If site roles cannot be retrieved
        """
        async with service as s:
            return await s.sites.get_site_roles(site_url=site_url)
    
    @mcp.tool()
    async def add_site_roles(site_url: str, roles: List[str]) -> Dict[str, Any]:
        """Add roles to a site.
        
        Args:
            site_url: The URL of the site
            roles: List of roles to add
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If roles cannot be added
        """
        async with service as s:
            return await s.sites.add_site_roles(site_url=site_url, roles=roles)
    
    @mcp.tool()
    async def remove_site_role(site_url: str, role: str) -> Dict[str, Any]:
        """Remove a role from a site.
        
        Args:
            site_url: The URL of the site
            role: The role to remove
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If role cannot be removed
        """
        async with service as s:
            return await s.sites.remove_site_role(site_url=site_url, role=role)
    
    @mcp.tool()
    async def get_site_moves(site_url: str) -> Dict[str, Any]:
        """Get site moves for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Information about site moves
            
        Raises:
            BingWebmasterError: If site moves cannot be retrieved
        """
        async with service as s:
            return await s.sites.get_site_moves(site_url=site_url)
    
    @mcp.tool()
    async def submit_site_move(site_url: str, new_url: str) -> Dict[str, Any]:
        """Submit a site move.
        
        Args:
            site_url: The current URL of the site
            new_url: The new URL of the site
            
        Returns:
            Dict[str, Any]: Result of the site move submission
            
        Raises:
            BingWebmasterError: If site move cannot be submitted
        """
        async with service as s:
            return await s.sites.submit_site_move(site_url=site_url, new_url=new_url)
    
    # Submission Tools
    @mcp.tool()
    async def submit_url_for_indexing(url: str) -> Dict[str, Any]:
        """Submit a URL to Bing for indexing.
        
        Args:
            url: The URL to submit for indexing
            
        Returns:
            Dict[str, Any]: Result of the URL submission
            
        Raises:
            BingWebmasterError: If URL cannot be submitted
        """
        async with service as s:
            return await s.submission.submit_url(url=url)
    
    @mcp.tool()
    async def submit_urls_batch(urls: List[str]) -> Dict[str, Any]:
        """Submit multiple URLs to Bing for indexing.
        
        Args:
            urls: List of URLs to submit for indexing
            
        Returns:
            Dict[str, Any]: Result of the batch URL submission
            
        Raises:
            BingWebmasterError: If URLs cannot be submitted
        """
        async with service as s:
            return await s.submission.submit_url_batch(urls=urls)
    
    @mcp.tool()
    async def submit_content(site_url: str, url: str, http_message: str, structured_data: str, dynamic_serving: int) -> Dict[str, Any]:
        """Submit content for a specific URL.
        
        Args:
            site_url: The URL of the site
            url: The specific URL to submit content for
            http_message: The HTTP message (base64 encoded)
            structured_data: Structured data (base64 encoded)
            dynamic_serving: Dynamic serving type (0-5)
            
        Returns:
            Dict[str, Any]: Result of the content submission
            
        Raises:
            BingWebmasterError: If content submission fails
        """
        async with service as s:
            return await s.submission.submit_content(
                site_url=site_url,
                url=url,
                http_message=http_message,
                structured_data=structured_data,
                dynamic_serving=dynamic_serving
            )
    
    @mcp.tool()
    async def submit_feed(site_url: str, feed_url: str) -> Dict[str, Any]:
        """Submit a feed for a site.
        
        Args:
            site_url: The URL of the site
            feed_url: The URL of the feed
            
        Returns:
            Dict[str, Any]: Result of the feed submission
            
        Raises:
            BingWebmasterError: If feed cannot be submitted
        """
        async with service as s:
            return await s.submission.submit_feed(site_url=site_url, feed_url=feed_url)
    
    @mcp.tool()
    async def get_feeds(site_url: str) -> Dict[str, Any]:
        """Get feeds for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: List of feeds for the site
            
        Raises:
            BingWebmasterError: If feeds cannot be retrieved
        """
        async with service as s:
            return await s.submission.get_feeds(site_url=site_url)
    
    @mcp.tool()
    async def get_feed_details(site_url: str, feed_url: str) -> Dict[str, Any]:
        """Get details for a feed.
        
        Args:
            site_url: The URL of the site
            feed_url: The URL of the feed
            
        Returns:
            Dict[str, Any]: Feed details
            
        Raises:
            BingWebmasterError: If feed details cannot be retrieved
        """
        async with service as s:
            return await s.submission.get_feed_details(site_url=site_url, feed_url=feed_url)
    
    @mcp.tool()
    async def remove_feed(site_url: str, feed_url: str) -> Dict[str, Any]:
        """Remove a feed from a site.
        
        Args:
            site_url: The URL of the site
            feed_url: The URL of the feed
            
        Returns:
            Dict[str, Any]: Result of the feed removal
            
        Raises:
            BingWebmasterError: If feed cannot be removed
        """
        async with service as s:
            return await s.submission.remove_feed(site_url=site_url, feed_url=feed_url)
    
    @mcp.tool()
    async def get_url_submission_quota(site_url: str) -> Dict[str, Any]:
        """Get URL submission quota for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: URL submission quota information
            
        Raises:
            BingWebmasterError: If quota cannot be retrieved
        """
        async with service as s:
            return await s.submission.get_url_submission_quota(site_url=site_url)
    
    @mcp.tool()
    async def get_content_submission_quota(site_url: str) -> Dict[str, Any]:
        """Get content submission quota for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Content submission quota information
            
        Raises:
            BingWebmasterError: If quota cannot be retrieved
        """
        async with service as s:
            return await s.submission.get_content_submission_quota(site_url=site_url)
    
    @mcp.tool()
    async def fetch_url(url: str) -> Dict[str, Any]:
        """Fetch a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Dict[str, Any]: Fetch result
            
        Raises:
            BingWebmasterError: If URL cannot be fetched
        """
        async with service as s:
            return await s.submission.fetch_url(url=url)
    
    @mcp.tool()
    async def get_fetched_urls(site_url: str) -> Dict[str, Any]:
        """Get fetched URLs for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: List of fetched URLs
            
        Raises:
            BingWebmasterError: If fetched URLs cannot be retrieved
        """
        async with service as s:
            return await s.submission.get_fetched_urls(site_url=site_url)
    
    @mcp.tool()
    async def get_fetched_url_details(site_url: str, url: str) -> Dict[str, Any]:
        """Get details for a fetched URL.
        
        Args:
            site_url: The URL of the site
            url: The URL to get details for
            
        Returns:
            Dict[str, Any]: Fetched URL details
            
        Raises:
            BingWebmasterError: If URL details cannot be retrieved
        """
        async with service as s:
            return await s.submission.get_fetched_url_details(site_url=site_url, url=url)
    
    # Traffic Analysis Tools
    @mcp.tool()
    async def get_query_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Query statistics data
            
        Raises:
            BingWebmasterError: If query stats cannot be retrieved
        """
        async with service as s:
            return await s.traffic.get_query_stats(site_url=site_url, start_date=start_date, end_date=end_date)
    
    @mcp.tool()
    async def get_query_traffic_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query traffic stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Query traffic statistics data
            
        Raises:
            BingWebmasterError: If query traffic stats cannot be retrieved
        """
        async with service as s:
            return await s.traffic.get_query_traffic_stats(site_url=site_url, start_date=start_date, end_date=end_date)
    
    @mcp.tool()
    async def get_query_page_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query page stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Query page statistics data
            
        Raises:
            BingWebmasterError: If query page stats cannot be retrieved
        """
        async with service as s:
            return await s.traffic.get_query_page_stats(site_url=site_url, start_date=start_date, end_date=end_date)
    
    @mcp.tool()
    async def get_query_page_detail_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query page detail stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Query page detail statistics data
            
        Raises:
            BingWebmasterError: If query page detail stats cannot be retrieved
        """
        async with service as s:
            return await s.traffic.get_query_page_detail_stats(site_url=site_url, start_date=start_date, end_date=end_date)
    
    @mcp.tool()
    async def get_page_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get page stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Page statistics data
            
        Raises:
            BingWebmasterError: If page stats cannot be retrieved
        """
        async with service as s:
            return await s.traffic.get_page_stats(site_url=site_url, start_date=start_date, end_date=end_date)
    
    @mcp.tool()
    async def get_page_query_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get page query stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Page query statistics data
            
        Raises:
            BingWebmasterError: If page query stats cannot be retrieved
        """
        async with service as s:
            return await s.traffic.get_page_query_stats(site_url=site_url, start_date=start_date, end_date=end_date)
    
    @mcp.tool()
    async def get_rank_and_traffic_stats(site_url: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get rank and traffic stats for a site.
        
        Args:
            site_url: The URL of the site
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Rank and traffic statistics data
            
        Raises:
            BingWebmasterError: If rank and traffic stats cannot be retrieved
        """
        async with service as s:
            return await s.traffic.get_rank_and_traffic_stats(site_url=site_url, start_date=start_date, end_date=end_date)
    
    # Crawling Tools
    @mcp.tool()
    async def get_crawl_stats(site_url: str) -> List[Dict[str, Any]]:
        """Get crawl stats for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            List[Dict[str, Any]]: List of daily crawl statistics
            
        Raises:
            BingWebmasterError: If crawl stats cannot be retrieved
        """
        async with service as s:
            return await s.crawling.get_crawl_stats(site_url=site_url)
    
    @mcp.tool()
    async def get_crawl_settings(site_url: str) -> Dict[str, Any]:
        """Get crawl settings for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: The current crawl settings for the site
            
        Raises:
            BingWebmasterError: If crawl settings cannot be retrieved
        """
        async with service as s:
            return await s.crawling.get_crawl_settings(site_url=site_url)
    
    @mcp.tool()
    async def save_crawl_settings(site_url: str, settings: Dict[str, Any]) -> None:
        """Save crawl settings for a site.
        
        Args:
            site_url: The URL of the site
            settings: The new crawl settings to apply
            
        Returns:
            None
            
        Raises:
            BingWebmasterError: If crawl settings cannot be saved
        """
        async with service as s:
            return await s.crawling.save_crawl_settings(site_url=site_url, settings=settings)
    
    @mcp.tool()
    async def get_crawl_issues(site_url: str) -> List[Dict[str, Any]]:
        """Get crawl issues for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            List[Dict[str, Any]]: List of URLs with their associated crawl issues
            
        Raises:
            BingWebmasterError: If crawl issues cannot be retrieved
        """
        async with service as s:
            return await s.crawling.get_crawl_issues(site_url=site_url)
    
    # Keyword Analysis Tools
    @mcp.tool()
    async def get_keyword(query: str, country: str, language: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get keyword impressions for a selected period.
        
        Args:
            query: The keyword query
            country: The country code
            language: The language code
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            Dict[str, Any]: Keyword impression data, or None if no data available
            
        Raises:
            BingWebmasterError: If keyword data cannot be retrieved
        """
        async with service as s:
            return await s.keywords.get_keyword(
                query=query, 
                country=country, 
                language=language, 
                start_date=start_date, 
                end_date=end_date
            )
    
    @mcp.tool()
    async def get_keyword_stats(query: str, country: str, language: str) -> List[Dict[str, Any]]:
        """Retrieve keyword statistics for a specific query.
        
        Args:
            query: The keyword query
            country: The country code (i.e. gb)
            language: The language and country code (i.e. en-GB)
            
        Returns:
            List[Dict[str, Any]]: List of keyword statistics
            
        Raises:
            BingWebmasterError: If statistics cannot be retrieved
        """
        async with service as s:
            return await s.keywords.get_keyword_stats(
                query=query, 
                country=country, 
                language=language
            )
    
    @mcp.tool()
    async def get_related_keywords(query: str, country: str, language: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get keyword impressions for related keywords in the selected period.
        
        Args:
            query: The base keyword query
            country: The country code
            language: The language code
            start_date: The start date in YYYY-MM-DD format
            end_date: The end date in YYYY-MM-DD format
            
        Returns:
            List[Dict[str, Any]]: List of related keywords and their impression data
            
        Raises:
            BingWebmasterError: If related keywords cannot be retrieved
        """
        async with service as s:
            return await s.keywords.get_related_keywords(
                query=query, 
                country=country, 
                language=language, 
                start_date=start_date, 
                end_date=end_date
            )
    
    # Link Analysis Tools
    @mcp.tool()
    async def get_link_counts(site_url: str) -> Dict[str, Any]:
        """Get link counts for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Link counts data
            
        Raises:
            BingWebmasterError: If link counts cannot be retrieved
        """
        async with service as s:
            return await s.links.get_link_counts(site_url=site_url)
    
    @mcp.tool()
    async def get_url_links(site_url: str, url: str) -> Dict[str, Any]:
        """Get links for a URL.
        
        Args:
            site_url: The URL of the site
            url: The URL to get links for
            
        Returns:
            Dict[str, Any]: URL links data
            
        Raises:
            BingWebmasterError: If URL links cannot be retrieved
        """
        async with service as s:
            return await s.links.get_url_links(site_url=site_url, url=url)
    
    @mcp.tool()
    async def get_deep_link(site_url: str, url: str) -> Dict[str, Any]:
        """Get deep link for a URL.
        
        Args:
            site_url: The URL of the site
            url: The URL to get deep link for
            
        Returns:
            Dict[str, Any]: Deep link data
            
        Raises:
            BingWebmasterError: If deep link cannot be retrieved
        """
        async with service as s:
            return await s.links.get_deep_link(site_url=site_url, url=url)
    
    @mcp.tool()
    async def get_deep_link_blocks(site_url: str) -> Dict[str, Any]:
        """Get deep link blocks for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Deep link blocks data
            
        Raises:
            BingWebmasterError: If deep link blocks cannot be retrieved
        """
        async with service as s:
            return await s.links.get_deep_link_blocks(site_url=site_url)
    
    @mcp.tool()
    async def add_deep_link_block(site_url: str, url: str) -> Dict[str, Any]:
        """Add a deep link block for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to block
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If deep link block cannot be added
        """
        async with service as s:
            return await s.links.add_deep_link_block(site_url=site_url, url=url)
    
    @mcp.tool()
    async def remove_deep_link_block(site_url: str, url: str) -> Dict[str, Any]:
        """Remove a deep link block for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to unblock
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If deep link block cannot be removed
        """
        async with service as s:
            return await s.links.remove_deep_link_block(site_url=site_url, url=url)
    
    @mcp.tool()
    async def update_deep_link(site_url: str, url: str, deep_link: str) -> Dict[str, Any]:
        """Update a deep link for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to update deep link for
            deep_link: The new deep link
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If deep link cannot be updated
        """
        async with service as s:
            return await s.links.update_deep_link(site_url=site_url, url=url, deep_link=deep_link)
    
    @mcp.tool()
    async def get_deep_link_algo_urls(site_url: str) -> Dict[str, Any]:
        """Get deep link algorithm URLs for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Deep link algorithm URLs data
            
        Raises:
            BingWebmasterError: If deep link algorithm URLs cannot be retrieved
        """
        async with service as s:
            return await s.links.get_deep_link_algo_urls(site_url=site_url)
    
    @mcp.tool()
    async def get_connected_pages(site_url: str) -> Dict[str, Any]:
        """Get connected pages for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Connected pages data
            
        Raises:
            BingWebmasterError: If connected pages cannot be retrieved
        """
        async with service as s:
            return await s.links.get_connected_pages(site_url=site_url)
    
    @mcp.tool()
    async def add_connected_page(site_url: str, url: str) -> Dict[str, Any]:
        """Add a connected page for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to add as a connected page
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If connected page cannot be added
        """
        async with service as s:
            return await s.links.add_connected_page(site_url=site_url, url=url)
    
    # Content Management Tools
    @mcp.tool()
    async def get_url_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get URL info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get info for
            
        Returns:
            Dict[str, Any]: URL information data
            
        Raises:
            BingWebmasterError: If URL info cannot be retrieved
        """
        async with service as s:
            return await s.content.get_url_info(site_url=site_url, url=url)
    
    @mcp.tool()
    async def get_url_traffic_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get URL traffic info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get traffic info for
            
        Returns:
            Dict[str, Any]: URL traffic information data
            
        Raises:
            BingWebmasterError: If URL traffic info cannot be retrieved
        """
        async with service as s:
            return await s.content.get_url_traffic_info(site_url=site_url, url=url)
    
    @mcp.tool()
    async def get_children_url_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get children URL info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get children info for
            
        Returns:
            Dict[str, Any]: Children URL information data
            
        Raises:
            BingWebmasterError: If children URL info cannot be retrieved
        """
        async with service as s:
            return await s.content.get_children_url_info(site_url=site_url, url=url)
    
    @mcp.tool()
    async def get_children_url_traffic_info(site_url: str, url: str) -> Dict[str, Any]:
        """Get children URL traffic info for a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to get children traffic info for
            
        Returns:
            Dict[str, Any]: Children URL traffic information data
            
        Raises:
            BingWebmasterError: If children URL traffic info cannot be retrieved
        """
        async with service as s:
            return await s.content.get_children_url_traffic_info(site_url=site_url, url=url)
    
    # Content Blocking Tools
    @mcp.tool()
    async def get_blocked_urls(site_url: str) -> Dict[str, Any]:
        """Get a list of blocked pages/directories for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: List of blocked URLs and their settings
            
        Raises:
            BingWebmasterError: If blocked URLs cannot be retrieved
        """
        async with service as s:
            return await s.blocking.get_blocked_urls(site_url=site_url)
    
    @mcp.tool()
    async def add_blocked_url(site_url: str, url: str, entity_type: str = "Page", date: Optional[str] = None) -> Dict[str, Any]:
        """Add a blocked URL to a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to be blocked
            entity_type: The type of entity to block (Page or Directory)
            date: The date the URL was blocked (default: current date)
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If URL cannot be blocked
        """
        async with service as s:
            return await s.blocking.add_blocked_url(site_url=site_url, blocked_url=url, entity_type=entity_type, date=date)
    
    @mcp.tool()
    async def remove_blocked_url(site_url: str, url: str, entity_type: str = "Page", date: Optional[str] = None) -> Dict[str, Any]:
        """Remove a blocked URL from a site.
        
        Args:
            site_url: The URL of the site
            url: The URL to be unblocked
            entity_type: The type of entity to unblock (Page or Directory)
            date: The date the URL was blocked
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If URL cannot be unblocked
        """
        async with service as s:
            return await s.blocking.remove_blocked_url(site_url=site_url, blocked_url=url, entity_type=entity_type, date=date)
    
    @mcp.tool()
    async def get_active_page_preview_blocks(site_url: str) -> Dict[str, Any]:
        """Get active page preview blocks for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: List of active page preview blocks
            
        Raises:
            BingWebmasterError: If preview blocks cannot be retrieved
        """
        async with service as s:
            return await s.blocking.get_active_page_preview_blocks(site_url=site_url)
    
    @mcp.tool()
    async def add_page_preview_block(site_url: str, url: str, reason: str) -> Dict[str, Any]:
        """Add a page preview block.
        
        Args:
            site_url: The URL of the site
            url: The URL to block from page preview
            reason: The reason for blocking the page preview
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If preview block cannot be added
        """
        async with service as s:
            return await s.blocking.add_page_preview_block(site_url=site_url, url=url, reason=reason)
    
    @mcp.tool()
    async def remove_page_preview_block(site_url: str, url: str) -> Dict[str, Any]:
        """Remove a page preview block.
        
        Args:
            site_url: The URL of the site
            url: The URL to remove the page preview block from
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If preview block cannot be removed
        """
        async with service as s:
            return await s.blocking.remove_page_preview_block(site_url=site_url, url=url)
    
    # Regional Settings Tools
    @mcp.tool()
    async def get_country_region_settings(site_url: str) -> Dict[str, Any]:
        """Get country region settings for a site.
        
        Args:
            site_url: The URL of the site
            
        Returns:
            Dict[str, Any]: Country region settings data
            
        Raises:
            BingWebmasterError: If country region settings cannot be retrieved
        """
        async with service as s:
            return await s.regional.get_country_region_settings(site_url=site_url)
    
    @mcp.tool()
    async def add_country_region_settings(site_url: str, country: str, region: str) -> Dict[str, Any]:
        """Add country region settings for a site.
        
        Args:
            site_url: The URL of the site
            country: The country code
            region: The region code
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If country region settings cannot be added
        """
        async with service as s:
            return await s.regional.add_country_region_settings(site_url=site_url, country=country, region=region)
    
    @mcp.tool()
    async def remove_country_region_settings(site_url: str, country: str, region: str) -> Dict[str, Any]:
        """Remove country region settings for a site.
        
        Args:
            site_url: The URL of the site
            country: The country code
            region: The region code
            
        Returns:
            Dict[str, Any]: Result of the operation
            
        Raises:
            BingWebmasterError: If country region settings cannot be removed
        """
        async with service as s:
            return await s.regional.remove_country_region_settings(site_url=site_url, country=country, region=region) 