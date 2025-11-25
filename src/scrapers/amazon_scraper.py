import re
from typing import Optional
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    """Scraper specifically designed for Amazon product pages"""

    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Amazon product page"""
        price_selectors = [
            {'class': 'a-price-whole'},
            {'class': 'a-offscreen'},
            {'id': 'priceblock_ourprice'},
            {'id': 'priceblock_dealprice'},
            {'class': 'priceToPay'}
        ]

        for selector in price_selectors:
            price_element = soup.find('span', selector)
            if price_element:
                price_text = price_element.get_text().strip()
                # Remove currency symbols and extract numbers
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        return float(price_match.group())
                    except ValueError:
                        continue

        return None

    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title from Amazon"""
        title_selectors = [
            {'id': 'productTitle'},
            {'class': 'product-title-word-break'}
        ]

        for selector in title_selectors:
            title_element = soup.find(['h1', 'span'], selector)
            if title_element:
                return title_element.get_text().strip()

        return None

    def extract_availability(self, soup: BeautifulSoup) -> bool:
        """Check if product is available on Amazon"""
        availability_element = soup.find('div', {'id': 'availability'})
        if availability_element:
            availability_text = availability_element.get_text().lower()
            if 'out of stock' in availability_text or 'unavailable' in availability_text:
                return False
        return True
