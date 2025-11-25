#!/usr/bin/env python3
"""
E-commerce Price Tracker - Main Application
Automated price monitoring with alerts and visualization
"""

import sys
import logging
import argparse
from datetime import datetime

import config
from src.scrapers import ScraperFactory
from src.database import DatabaseManager
from src.notifications import EmailNotifier
from src.visualization import PriceChartGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/price_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PriceTracker:
    """Main price tracking application"""

    def __init__(self):
        self.db = DatabaseManager(config.DATABASE_PATH)
        self.notifier = EmailNotifier(
            config.EMAIL_SENDER,
            config.EMAIL_PASSWORD,
            config.EMAIL_RECEIVER
        )
        self.chart_generator = PriceChartGenerator(config.CHART_OUTPUT_DIR)

    def track_product(self, product_name: str, urls: dict, target_price: float = None) -> dict:
        """
        Track a single product across multiple sites

        Args:
            product_name: Name of the product
            urls: Dictionary of site_name: url pairs
            target_price: Optional target price for alerts

        Returns:
            Dictionary with tracking results
        """
        logger.info(f"Tracking: {product_name}")
        results = {
            'product': product_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prices': {},
            'alerts': []
        }

        for site_key, url in urls.items():
            try:
                # Get appropriate scraper
                scraper = ScraperFactory.get_scraper(url, config.MAX_RETRIES, config.REQUEST_TIMEOUT)
                if not scraper:
                    logger.warning(f"No scraper available for {url}")
                    continue

                # Scrape product data
                product_data = scraper.scrape_product(url)
                if not product_data:
                    logger.warning(f"Failed to scrape {url}")
                    continue

                # Store in database
                site_name = ScraperFactory.get_site_name(url)
                price_changed = self.db.add_price_record(
                    product_name=product_name,
                    site=site_name,
                    price=product_data['price'],
                    title=product_data['title'],
                    url=url,
                    available=product_data['available']
                )

                results['prices'][site_name] = product_data['price']

                # Check for price drops
                if price_changed:
                    drop_info = self.db.check_price_drop(
                        product_name,
                        site_name,
                        config.PRICE_DROP_PERCENTAGE,
                        config.PRICE_DROP_AMOUNT
                    )

                    if drop_info:
                        logger.info(f"Price drop detected: {drop_info}")
                        results['alerts'].append(drop_info)

                        # Send email notification
                        self.notifier.send_price_drop_alert(drop_info)

                # Check if target price reached
                if target_price and product_data['price'] <= target_price:
                    logger.info(f"Target price reached for {product_name} at {site_name}!")
                    # Could send special notification here

            except Exception as e:
                logger.error(f"Error tracking {product_name} at {site_key}: {str(e)}")

        return results

    def track_all_products(self):
        """Track all products configured in config.py"""
        logger.info("Starting tracking run for all products")
        all_results = []

        for product in config.PRODUCTS_TO_TRACK:
            result = self.track_product(
                product['name'],
                product['urls'],
                product.get('target_price')
            )
            all_results.append(result)

        logger.info(f"Completed tracking {len(all_results)} products")
        return all_results

    def generate_reports(self, product_name: str = None, days: int = 30):
        """
        Generate price charts and export data

        Args:
            product_name: Optional product name to filter
            days: Number of days of history to include
        """
        logger.info("Generating reports...")

        if product_name:
            products = [product_name]
        else:
            products = self.db.get_all_products()

        for product in products:
            try:
                # Get price history
                df = self.db.get_price_history(product, days=days)

                if df.empty:
                    logger.warning(f"No data found for {product}")
                    continue

                # Generate charts
                self.chart_generator.plot_price_history(df, product)
                self.chart_generator.plot_price_comparison(df, product)

                # Find target price if configured
                target_price = None
                for p in config.PRODUCTS_TO_TRACK:
                    if p['name'] == product:
                        target_price = p.get('target_price')
                        break

                self.chart_generator.plot_savings_tracker(df, product, target_price)

                logger.info(f"Generated charts for {product}")

            except Exception as e:
                logger.error(f"Error generating reports for {product}: {str(e)}")

    def export_data(self, format: str = 'csv', product_name: str = None):
        """
        Export price data to file

        Args:
            format: 'csv' or 'json'
            product_name: Optional product to filter
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if product_name:
            filename = f"{product_name.replace(' ', '_')}_{timestamp}.{format}"
        else:
            filename = f"all_products_{timestamp}.{format}"

        output_path = f"{config.CSV_OUTPUT_DIR}/{filename}"

        if format == 'csv':
            self.db.export_to_csv(output_path, product_name)
        elif format == 'json':
            self.db.export_to_json(output_path, product_name)
        else:
            logger.error(f"Unsupported format: {format}")
            return

        logger.info(f"Data exported to {output_path}")
        return output_path

    def print_summary(self):
        """Print summary of tracked products and latest prices"""
        products = self.db.get_all_products()

        if not products:
            print("\nNo products are currently being tracked.")
            return

        print("\n" + "="*80)
        print("PRICE TRACKER SUMMARY".center(80))
        print("="*80 + "\n")

        for product in products:
            latest_prices = self.db.get_latest_prices(product)

            if not latest_prices:
                continue

            print(f"📦 {product}")
            print("-" * 80)

            for site, data in latest_prices.items():
                print(f"  {site:15s} ${data['price']:8.2f}  (updated: {data['timestamp']})")

            print()


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description='E-commerce Price Tracker - Monitor prices and get alerts'
    )

    parser.add_argument(
        '--track',
        action='store_true',
        help='Run price tracking for all configured products'
    )

    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate price charts and reports'
    )

    parser.add_argument(
        '--export',
        choices=['csv', 'json'],
        help='Export price data to CSV or JSON'
    )

    parser.add_argument(
        '--product',
        type=str,
        help='Specific product name to track/report/export'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days of history for reports (default: 30)'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='Display summary of tracked products'
    )

    args = parser.parse_args()

    # Create tracker instance
    tracker = PriceTracker()

    # Execute based on arguments
    if args.track:
        if args.product:
            # Track specific product
            for p in config.PRODUCTS_TO_TRACK:
                if p['name'] == args.product:
                    tracker.track_product(p['name'], p['urls'], p.get('target_price'))
                    break
            else:
                print(f"Product '{args.product}' not found in configuration")
        else:
            # Track all products
            tracker.track_all_products()

    if args.report:
        tracker.generate_reports(args.product, args.days)

    if args.export:
        tracker.export_data(args.export, args.product)

    if args.summary:
        tracker.print_summary()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "="*80)
        print("QUICK START EXAMPLES:")
        print("="*80)
        print("\n1. Track all products:")
        print("   python price_tracker.py --track")
        print("\n2. Generate reports:")
        print("   python price_tracker.py --report")
        print("\n3. Export data to CSV:")
        print("   python price_tracker.py --export csv")
        print("\n4. View summary:")
        print("   python price_tracker.py --summary")
        print("\n5. Combine multiple actions:")
        print("   python price_tracker.py --track --report --export json")
        print()


if __name__ == '__main__':
    main()
