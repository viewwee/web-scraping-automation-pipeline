import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER', '')

# Scraping Configuration
SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 12))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))

# Price Alert Configuration
PRICE_DROP_PERCENTAGE = float(os.getenv('PRICE_DROP_PERCENTAGE', 5))
PRICE_DROP_AMOUNT = float(os.getenv('PRICE_DROP_AMOUNT', 10))

# Telegram Configuration (Optional)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Database Configuration
DATABASE_PATH = 'data/price_tracker.db'

# Output Paths
CSV_OUTPUT_DIR = 'data/outputs'
JSON_OUTPUT_DIR = 'data/outputs'
CHART_OUTPUT_DIR = 'data/outputs'
LOG_DIR = 'logs'

# Products to Track (can be moved to JSON file for easier management)
PRODUCTS_TO_TRACK = [
    {
        'name': 'iPhone 15 Pro',
        'urls': {
            'amazon': 'https://www.amazon.com/dp/B0CHX1W1XY',
            'bestbuy': 'https://www.bestbuy.com/site/apple-iphone-15-pro-256gb/6525409.p'
        },
        'target_price': 999.00
    },
    {
        'name': 'Sony WH-1000XM5 Headphones',
        'urls': {
            'amazon': 'https://www.amazon.com/dp/B09XS7JWHH',
            'bestbuy': 'https://www.bestbuy.com/site/sony-wh-1000xm5-wireless-noise-canceling-headphones/6505727.p'
        },
        'target_price': 349.99
    }
]

# User Agent for requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]
