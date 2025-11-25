#!/usr/bin/env python3
"""
Demo script to generate sample data for portfolio showcase
Creates realistic price tracking data without actually scraping
"""

import random
from datetime import datetime, timedelta
import logging

from src.database import DatabaseManager
from src.visualization import PriceChartGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_demo_data():
    """Generate realistic demo data for portfolio"""

    db = DatabaseManager('data/price_tracker.db')

    # Demo products
    demo_products = [
        {
            'name': 'Sony WH-1000XM5 Headphones',
            'base_prices': {'Amazon': 399.99, 'Best Buy': 399.99},
            'volatility': 0.05  # 5% price variation
        },
        {
            'name': 'Apple AirPods Pro (2nd Gen)',
            'base_prices': {'Amazon': 249.99, 'Best Buy': 249.99},
            'volatility': 0.08
        },
        {
            'name': 'Samsung 55" 4K Smart TV',
            'base_prices': {'Amazon': 699.99, 'Best Buy': 729.99},
            'volatility': 0.10
        },
        {
            'name': 'Nintendo Switch OLED',
            'base_prices': {'Amazon': 349.99, 'Best Buy': 349.99},
            'volatility': 0.03
        },
        {
            'name': 'Dyson V15 Vacuum',
            'base_prices': {'Amazon': 649.99, 'Best Buy': 649.99},
            'volatility': 0.07
        }
    ]

    # Generate 30 days of price history
    days_back = 30
    base_date = datetime.now() - timedelta(days=days_back)

    logger.info("Generating demo price data...")

    for product in demo_products:
        logger.info(f"Creating data for: {product['name']}")

        for site, base_price in product['base_prices'].items():
            current_price = base_price

            for day in range(days_back + 1):
                # Add some realistic price movements
                # Prices generally trend down slightly over time (sales)
                trend = -0.002 * day  # 0.2% decrease per day

                # Add random volatility
                volatility = random.uniform(-product['volatility'], product['volatility'])

                # Occasionally have bigger price drops (sales events)
                if random.random() < 0.15:  # 15% chance
                    volatility -= random.uniform(0.05, 0.15)  # 5-15% drop

                # Calculate price
                price_factor = 1 + trend + volatility
                current_price = base_price * price_factor

                # Round to .99 or .95 like real stores
                current_price = round(current_price - 0.01, 2)
                if random.random() < 0.3:
                    current_price = round(current_price - 0.04, 2)

                # Add record with timestamp
                timestamp = base_date + timedelta(days=day, hours=random.randint(8, 20))

                # Simulate records (we'll manually insert to control timestamps)
                product_id = db.add_product(product['name'])

                # Direct SQL insert to control timestamp
                import sqlite3
                with sqlite3.connect(db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO price_history
                        (product_id, site, price, title, url, available, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product_id,
                        site,
                        current_price,
                        product['name'],
                        f'https://example.com/{product["name"].replace(" ", "-").lower()}',
                        True,
                        timestamp
                    ))
                    conn.commit()

    logger.info("Demo data generation complete!")
    logger.info(f"Generated {days_back + 1} days of data for {len(demo_products)} products")


def generate_demo_charts():
    """Generate charts from demo data"""

    logger.info("Generating demo charts...")

    db = DatabaseManager('data/price_tracker.db')
    chart_gen = PriceChartGenerator('data/outputs')

    products = db.get_all_products()

    for product in products:
        logger.info(f"Creating charts for: {product}")

        # Get price history
        df = db.get_price_history(product, days=30)

        if df.empty:
            continue

        # Generate all chart types
        chart_gen.plot_price_history(df, product)
        chart_gen.plot_price_comparison(df, product)
        chart_gen.plot_savings_tracker(df, product, target_price=None)

    logger.info("Demo charts generated successfully!")


def export_demo_data():
    """Export demo data to CSV and JSON"""

    logger.info("Exporting demo data...")

    db = DatabaseManager('data/price_tracker.db')

    # Export all data
    db.export_to_csv('data/outputs/demo_all_products.csv')
    db.export_to_json('data/outputs/demo_all_products.json')

    # Export individual products
    products = db.get_all_products()
    for product in products:
        safe_name = product.replace(' ', '_').replace('(', '').replace(')', '')
        db.export_to_csv(f'data/outputs/demo_{safe_name}.csv', product)

    logger.info("Demo data exported successfully!")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("DEMO DATA GENERATOR - Portfolio Showcase")
    print("="*80 + "\n")

    print("This script will generate realistic price tracking data for demonstration.")
    print("It will create:")
    print("  - 30 days of price history for 5 products")
    print("  - Price trend charts and visualizations")
    print("  - Sample CSV and JSON exports")
    print()

    response = input("Continue? (y/n): ")

    if response.lower() == 'y':
        generate_demo_data()
        generate_demo_charts()
        export_demo_data()

        print("\n" + "="*80)
        print("DEMO GENERATION COMPLETE!")
        print("="*80)
        print("\nGenerated files:")
        print("  - Database: data/price_tracker.db")
        print("  - Charts: data/outputs/*.png")
        print("  - Data exports: data/outputs/*.csv and *.json")
        print("\nYou can now showcase these files in your portfolio!")
        print()
    else:
        print("Demo generation cancelled.")
