from typing import Any, Callable, TypeVar
from functools import wraps
import inspect
from mcp.server.fastmcp import FastMCP
from mcp_server_bwt.services.bing_webmaster import BingWebmasterService
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

T = TypeVar('T')

# Map service attribute names to their corresponding service classes
SERVICE_CLASSES = {
    'sites': site_management.SiteManagementService,
    'submission': submission.SubmissionService,
    'traffic': traffic_analysis.TrafficAnalysisService,
    'crawling': crawling.CrawlingService,
    'keywords': keyword_analysis.KeywordAnalysisService,
    'links': link_analysis.LinkAnalysisService,
    'content': content_management.ContentManagementService,
    'blocking': content_blocking.ContentBlockingService,
    'regional': regional_settings.RegionalSettingsService,
    'urls': url_management.UrlManagementService
}

def wrap_service_method(mcp: FastMCP, service: BingWebmasterService, service_attr: str, method_name: str) -> Callable:
    """Helper function to wrap a service method with mcp.tool() while preserving its signature and docstring.
    
    Args:
        mcp: The MCP server instance
        service: The BingWebmasterService instance
        service_attr: The service attribute name (e.g., 'sites', 'submission')
        method_name: The method name to wrap
        
    Returns:
        The wrapped method as an MCP tool
    """
    # Get the service class from our mapping
    service_class = SERVICE_CLASSES[service_attr]
    # Get the original method
    original_method = getattr(service_class, method_name)
    # Get the signature
    sig = inspect.signature(original_method)
    # Remove 'self' parameter from signature
    parameters = list(sig.parameters.values())[1:]  # Skip 'self'
    
    # Create new signature without 'self'
    new_sig = sig.replace(parameters=parameters)
    
    # Create wrapper function with same signature
    @mcp.tool()
    @wraps(original_method)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Filter out any 'self' arguments that might be passed by the MCP client
        kwargs = {k: v for k, v in kwargs.items() if k != 'self'}
        
        async with service as s:
            service_obj = getattr(s, service_attr)
            # Get the method from the instance
            method = getattr(service_obj, method_name)
            # Call the method directly - it's already bound to the instance
            return await method(*args, **kwargs)
            
    # Copy signature and docstring
    wrapper.__signature__ = new_sig  # type: ignore
    wrapper.__doc__ = original_method.__doc__
    
    return wrapper

def add_bing_webmaster_tools(mcp: FastMCP, service: BingWebmasterService):
    # Site Management Tools
    list_verified_sites = wrap_service_method(mcp, service, 'sites', 'get_sites')
    add_site = wrap_service_method(mcp, service, 'sites', 'add_site')
    verify_site = wrap_service_method(mcp, service, 'sites', 'verify_site')
    remove_site = wrap_service_method(mcp, service, 'sites', 'remove_site')
    get_site_roles = wrap_service_method(mcp, service, 'sites', 'get_site_roles')
    add_site_roles = wrap_service_method(mcp, service, 'sites', 'add_site_roles')
    remove_site_role = wrap_service_method(mcp, service, 'sites', 'remove_site_role')
    get_site_moves = wrap_service_method(mcp, service, 'sites', 'get_site_moves')
    submit_site_move = wrap_service_method(mcp, service, 'sites', 'submit_site_move')
    
    # Submission Tools
    submit_url_for_indexing = wrap_service_method(mcp, service, 'submission', 'submit_url')
    submit_urls_batch = wrap_service_method(mcp, service, 'submission', 'submit_url_batch')
    submit_content = wrap_service_method(mcp, service, 'submission', 'submit_content')
    submit_feed = wrap_service_method(mcp, service, 'submission', 'submit_feed')
    get_feeds = wrap_service_method(mcp, service, 'submission', 'get_feeds')
    get_feed_details = wrap_service_method(mcp, service, 'submission', 'get_feed_details')
    remove_feed = wrap_service_method(mcp, service, 'submission', 'remove_feed')
    get_url_submission_quota = wrap_service_method(mcp, service, 'submission', 'get_url_submission_quota')
    get_content_submission_quota = wrap_service_method(mcp, service, 'submission', 'get_content_submission_quota')
    fetch_url = wrap_service_method(mcp, service, 'submission', 'fetch_url')
    get_fetched_urls = wrap_service_method(mcp, service, 'submission', 'get_fetched_urls')
    get_fetched_url_details = wrap_service_method(mcp, service, 'submission', 'get_fetched_url_details')
    
    # Traffic Analysis Tools
    get_query_stats = wrap_service_method(mcp, service, 'traffic', 'get_query_stats')
    get_query_traffic_stats = wrap_service_method(mcp, service, 'traffic', 'get_query_traffic_stats')
    get_query_page_stats = wrap_service_method(mcp, service, 'traffic', 'get_query_page_stats')
    get_query_page_detail_stats = wrap_service_method(mcp, service, 'traffic', 'get_query_page_detail_stats')
    get_page_stats = wrap_service_method(mcp, service, 'traffic', 'get_page_stats')
    get_page_query_stats = wrap_service_method(mcp, service, 'traffic', 'get_page_query_stats')
    get_rank_and_traffic_stats = wrap_service_method(mcp, service, 'traffic', 'get_rank_and_traffic_stats')
    
    # Crawling Tools
    get_crawl_stats = wrap_service_method(mcp, service, 'crawling', 'get_crawl_stats')
    get_crawl_settings = wrap_service_method(mcp, service, 'crawling', 'get_crawl_settings')
    save_crawl_settings = wrap_service_method(mcp, service, 'crawling', 'save_crawl_settings')
    get_crawl_issues = wrap_service_method(mcp, service, 'crawling', 'get_crawl_issues')
    
    # Keyword Analysis Tools
    get_keyword = wrap_service_method(mcp, service, 'keywords', 'get_keyword')
    get_keyword_stats = wrap_service_method(mcp, service, 'keywords', 'get_keyword_stats')
    get_related_keywords = wrap_service_method(mcp, service, 'keywords', 'get_related_keywords')
    
    # Link Analysis Tools
    get_link_counts = wrap_service_method(mcp, service, 'links', 'get_link_counts')
    get_url_links = wrap_service_method(mcp, service, 'links', 'get_url_links')
    get_deep_link = wrap_service_method(mcp, service, 'links', 'get_deep_link')
    get_deep_link_blocks = wrap_service_method(mcp, service, 'links', 'get_deep_link_blocks')
    add_deep_link_block = wrap_service_method(mcp, service, 'links', 'add_deep_link_block')
    remove_deep_link_block = wrap_service_method(mcp, service, 'links', 'remove_deep_link_block')
    update_deep_link = wrap_service_method(mcp, service, 'links', 'update_deep_link')
    get_deep_link_algo_urls = wrap_service_method(mcp, service, 'links', 'get_deep_link_algo_urls')
    get_connected_pages = wrap_service_method(mcp, service, 'links', 'get_connected_pages')
    add_connected_page = wrap_service_method(mcp, service, 'links', 'add_connected_page')
    
    # Content Management Tools
    get_url_info = wrap_service_method(mcp, service, 'content', 'get_url_info')
    get_url_traffic_info = wrap_service_method(mcp, service, 'content', 'get_url_traffic_info')
    get_children_url_info = wrap_service_method(mcp, service, 'content', 'get_children_url_info')
    get_children_url_traffic_info = wrap_service_method(mcp, service, 'content', 'get_children_url_traffic_info')
    
    # Content Blocking Tools
    get_blocked_urls = wrap_service_method(mcp, service, 'blocking', 'get_blocked_urls')
    add_blocked_url = wrap_service_method(mcp, service, 'blocking', 'add_blocked_url')
    remove_blocked_url = wrap_service_method(mcp, service, 'blocking', 'remove_blocked_url')
    get_active_page_preview_blocks = wrap_service_method(mcp, service, 'blocking', 'get_active_page_preview_blocks')
    add_page_preview_block = wrap_service_method(mcp, service, 'blocking', 'add_page_preview_block')
    remove_page_preview_block = wrap_service_method(mcp, service, 'blocking', 'remove_page_preview_block')
    
    # Regional Settings Tools
    get_country_region_settings = wrap_service_method(mcp, service, 'regional', 'get_country_region_settings')
    add_country_region_settings = wrap_service_method(mcp, service, 'regional', 'add_country_region_settings')
    remove_country_region_settings = wrap_service_method(mcp, service, 'regional', 'remove_country_region_settings')
    
    # URL Management Tools
    get_query_parameters = wrap_service_method(mcp, service, 'urls', 'get_query_parameters')
    add_query_parameter = wrap_service_method(mcp, service, 'urls', 'add_query_parameter')
    remove_query_parameter = wrap_service_method(mcp, service, 'urls', 'remove_query_parameter')
    enable_disable_query_parameter = wrap_service_method(mcp, service, 'urls', 'enable_disable_query_parameter')
