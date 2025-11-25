from typing import Optional
from .base_scraper import BaseScraper
from .amazon_scraper import AmazonScraper
from .bestbuy_scraper import BestBuyScraper


class ScraperFactory:
    """Factory class to create appropriate scraper based on URL"""

    @staticmethod
    def get_scraper(url: str, max_retries: int = 3, timeout: int = 30) -> Optional[BaseScraper]:
        """
        Return the appropriate scraper instance based on the URL

        Args:
            url: Product URL to scrape
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds

        Returns:
            BaseScraper instance or None if URL not supported
        """
        url_lower = url.lower()

        if 'amazon.com' in url_lower:
            return AmazonScraper(max_retries=max_retries, timeout=timeout)
        elif 'bestbuy.com' in url_lower:
            return BestBuyScraper(max_retries=max_retries, timeout=timeout)
        else:
            return None

    @staticmethod
    def get_site_name(url: str) -> str:
        """Extract site name from URL"""
        url_lower = url.lower()

        if 'amazon.com' in url_lower:
            return 'Amazon'
        elif 'bestbuy.com' in url_lower:
            return 'Best Buy'
        else:
            return 'Unknown'
