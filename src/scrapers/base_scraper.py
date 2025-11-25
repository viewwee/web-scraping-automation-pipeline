import time
import logging
import random
from abc import ABC, abstractmethod
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)


class BaseScraper(ABC):
    """Base class for all product scrapers"""

    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout
        self.ua = UserAgent()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()

    def get_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")

                # Add random delay to be respectful
                time.sleep(random.uniform(1, 3))

                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    timeout=self.timeout
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'lxml')
                self.logger.info(f"Successfully fetched {url}")
                return soup

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
                time.sleep(random.uniform(2, 5))

        return None

    @abstractmethod
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from parsed HTML - must be implemented by subclasses"""
        pass

    @abstractmethod
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title - must be implemented by subclasses"""
        pass

    def extract_availability(self, soup: BeautifulSoup) -> bool:
        """Extract availability status - can be overridden by subclasses"""
        return True

    def scrape_product(self, url: str) -> Optional[Dict]:
        """
        Main method to scrape product information
        Returns dict with price, title, availability, and timestamp
        """
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            price = self.extract_price(soup)
            title = self.extract_title(soup)
            availability = self.extract_availability(soup)

            if price is None:
                self.logger.warning(f"Could not extract price from {url}")
                return None

            result = {
                'price': price,
                'title': title or 'Unknown Product',
                'url': url,
                'available': availability,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            self.logger.info(f"Scraped: {title} - ${price}")
            return result

        except Exception as e:
            self.logger.error(f"Error extracting data from {url}: {str(e)}")
            return None
