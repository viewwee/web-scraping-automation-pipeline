import sqlite3
import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages price tracking database and data exports"""

    def __init__(self, db_path: str = 'data/price_tracker.db'):
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name)
                )
            ''')

            # Create price_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    site TEXT NOT NULL,
                    price REAL NOT NULL,
                    title TEXT,
                    url TEXT NOT NULL,
                    available BOOLEAN DEFAULT 1,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')

            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_price_history_product
                ON price_history(product_id, timestamp)
            ''')

            conn.commit()
            logger.info("Database initialized successfully")

    def add_product(self, product_name: str) -> int:
        """Add a product and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO products (name) VALUES (?)',
                (product_name,)
            )
            conn.commit()

            cursor.execute('SELECT id FROM products WHERE name = ?', (product_name,))
            return cursor.fetchone()[0]

    def add_price_record(self, product_name: str, site: str, price: float,
                        title: str, url: str, available: bool = True) -> bool:
        """
        Add a price record to the database

        Returns:
            bool: True if price changed from last record, False otherwise
        """
        product_id = self.add_product(product_name)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get last price for this product from this site
            cursor.execute('''
                SELECT price FROM price_history
                WHERE product_id = ? AND site = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (product_id, site))

            last_price_row = cursor.fetchone()
            price_changed = last_price_row is None or last_price_row[0] != price

            # Insert new price record
            cursor.execute('''
                INSERT INTO price_history
                (product_id, site, price, title, url, available, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_id, site, price, title, url, available, datetime.now()))

            conn.commit()
            logger.info(f"Added price record: {product_name} - {site} - ${price}")

            return price_changed

    def get_price_history(self, product_name: str, site: Optional[str] = None,
                         days: int = 30) -> pd.DataFrame:
        """
        Get price history for a product

        Args:
            product_name: Name of the product
            site: Optional site filter (Amazon, Best Buy, etc.)
            days: Number of days to look back

        Returns:
            pandas DataFrame with price history
        """
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT
                    ph.timestamp,
                    ph.site,
                    ph.price,
                    ph.title,
                    ph.url,
                    ph.available
                FROM price_history ph
                JOIN products p ON ph.product_id = p.id
                WHERE p.name = ?
                AND datetime(ph.timestamp) >= datetime('now', '-' || ? || ' days')
            '''

            params = [product_name, days]

            if site:
                query += ' AND ph.site = ?'
                params.append(site)

            query += ' ORDER BY ph.timestamp DESC'

            df = pd.read_sql_query(query, conn, params=params)
            return df

    def get_latest_prices(self, product_name: str) -> Dict[str, float]:
        """Get the latest price from each site for a product"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT ph.site, ph.price, ph.timestamp
                FROM price_history ph
                JOIN products p ON ph.product_id = p.id
                WHERE p.name = ?
                AND ph.id IN (
                    SELECT MAX(ph2.id)
                    FROM price_history ph2
                    JOIN products p2 ON ph2.product_id = p2.id
                    WHERE p2.name = ?
                    GROUP BY ph2.site
                )
            ''', (product_name, product_name))

            results = {}
            for row in cursor.fetchall():
                site, price, timestamp = row
                results[site] = {'price': price, 'timestamp': timestamp}

            return results

    def check_price_drop(self, product_name: str, site: str,
                        percentage_threshold: float = 5.0,
                        amount_threshold: float = 10.0) -> Optional[Dict]:
        """
        Check if there's a significant price drop

        Returns:
            Dict with drop info if significant drop detected, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT price, timestamp
                FROM price_history ph
                JOIN products p ON ph.product_id = p.id
                WHERE p.name = ? AND ph.site = ?
                ORDER BY timestamp DESC LIMIT 2
            ''', (product_name, site))

            prices = cursor.fetchall()

            if len(prices) < 2:
                return None

            current_price, current_time = prices[0]
            previous_price, previous_time = prices[1]

            price_diff = previous_price - current_price
            percentage_drop = (price_diff / previous_price) * 100

            if price_diff >= amount_threshold or percentage_drop >= percentage_threshold:
                return {
                    'product': product_name,
                    'site': site,
                    'previous_price': previous_price,
                    'current_price': current_price,
                    'amount_drop': price_diff,
                    'percentage_drop': percentage_drop,
                    'timestamp': current_time
                }

            return None

    def export_to_csv(self, output_path: str, product_name: Optional[str] = None):
        """Export price history to CSV"""
        with sqlite3.connect(self.db_path) as conn:
            if product_name:
                query = '''
                    SELECT
                        p.name as product_name,
                        ph.site,
                        ph.price,
                        ph.title,
                        ph.url,
                        ph.available,
                        ph.timestamp
                    FROM price_history ph
                    JOIN products p ON ph.product_id = p.id
                    WHERE p.name = ?
                    ORDER BY ph.timestamp DESC
                '''
                df = pd.read_sql_query(query, conn, params=[product_name])
            else:
                query = '''
                    SELECT
                        p.name as product_name,
                        ph.site,
                        ph.price,
                        ph.title,
                        ph.url,
                        ph.available,
                        ph.timestamp
                    FROM price_history ph
                    JOIN products p ON ph.product_id = p.id
                    ORDER BY p.name, ph.timestamp DESC
                '''
                df = pd.read_sql_query(query, conn)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(df)} records to {output_path}")

    def export_to_json(self, output_path: str, product_name: Optional[str] = None):
        """Export price history to JSON"""
        with sqlite3.connect(self.db_path) as conn:
            if product_name:
                query = '''
                    SELECT
                        p.name as product_name,
                        ph.site,
                        ph.price,
                        ph.title,
                        ph.url,
                        ph.available,
                        ph.timestamp
                    FROM price_history ph
                    JOIN products p ON ph.product_id = p.id
                    WHERE p.name = ?
                    ORDER BY ph.timestamp DESC
                '''
                df = pd.read_sql_query(query, conn, params=[product_name])
            else:
                query = '''
                    SELECT
                        p.name as product_name,
                        ph.site,
                        ph.price,
                        ph.title,
                        ph.url,
                        ph.available,
                        ph.timestamp
                    FROM price_history ph
                    JOIN products p ON ph.product_id = p.id
                    ORDER BY p.name, ph.timestamp DESC
                '''
                df = pd.read_sql_query(query, conn)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_json(output_path, orient='records', indent=2, date_format='iso')
            logger.info(f"Exported {len(df)} records to {output_path}")

    def get_all_products(self) -> List[str]:
        """Get list of all tracked products"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM products ORDER BY name')
            return [row[0] for row in cursor.fetchall()]
