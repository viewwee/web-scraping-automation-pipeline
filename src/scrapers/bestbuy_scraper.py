import re
from typing import Optional
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper


class BestBuyScraper(BaseScraper):
    """Scraper specifically designed for Best Buy product pages"""

    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Best Buy product page"""
        price_selectors = [
            {'class': 'priceView-customer-price'},
            {'class': 'priceView-hero-price'},
            {'data-testid': 'customer-price'},
            {'aria-label': re.compile(r'[Pp]rice')}
        ]

        for selector in price_selectors:
            price_element = soup.find(['span', 'div'], selector)
            if price_element:
                price_text = price_element.get_text().strip()
                # Extract numeric price
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text.replace(',', ''))
                if price_match:
                    try:
                        return float(price_match.group(1))
                    except ValueError:
                        continue

        # Try meta tags as fallback
        meta_price = soup.find('meta', {'property': 'product:price:amount'})
        if meta_price and meta_price.get('content'):
            try:
                return float(meta_price['content'])
            except ValueError:
                pass

        return None

    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title from Best Buy"""
        title_selectors = [
            {'class': 'sku-title'},
            {'data-testid': 'sku-title'},
            {'class': 'heading-5'}
        ]

        for selector in title_selectors:
            title_element = soup.find(['h1', 'span'], selector)
            if title_element:
                return title_element.get_text().strip()

        # Try meta tags as fallback
        meta_title = soup.find('meta', {'property': 'og:title'})
        if meta_title and meta_title.get('content'):
            return meta_title['content']

        return None

    def extract_availability(self, soup: BeautifulSoup) -> bool:
        """Check if product is available on Best Buy"""
        # Check for sold out button
        sold_out = soup.find(['button', 'span'], text=re.compile(r'Sold Out', re.IGNORECASE))
        if sold_out:
            return False

        # Check availability in structured data
        availability_element = soup.find('link', {'itemprop': 'availability'})
        if availability_element:
            availability_url = availability_element.get('href', '')
            if 'OutOfStock' in availability_url:
                return False

        return True
