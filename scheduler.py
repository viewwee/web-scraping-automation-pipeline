#!/usr/bin/env python3
"""
Automated Price Tracking Scheduler
Runs price tracking at specified intervals
"""

import schedule
import time
import logging
from datetime import datetime

import config
from price_tracker import PriceTracker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def scheduled_tracking_job():
    """Job to run on schedule"""
    logger.info("="*80)
    logger.info(f"Starting scheduled tracking job at {datetime.now()}")
    logger.info("="*80)

    try:
        tracker = PriceTracker()

        # Track all products
        results = tracker.track_all_products()

        # Log results
        for result in results:
            if result['alerts']:
                logger.info(f"Alerts generated for {result['product']}: {len(result['alerts'])}")

        # Generate reports weekly (on Sundays)
        if datetime.now().weekday() == 6:  # Sunday
            logger.info("Generating weekly reports...")
            tracker.generate_reports()

        logger.info("Scheduled job completed successfully")

    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}", exc_info=True)


def run_scheduler():
    """Start the scheduler with configured interval"""
    logger.info("Starting Price Tracker Scheduler")
    logger.info(f"Tracking interval: Every {config.SCRAPE_INTERVAL_HOURS} hours")
    logger.info(f"Tracking {len(config.PRODUCTS_TO_TRACK)} products")
    logger.info("-" * 80)

    # Schedule the job
    schedule.every(config.SCRAPE_INTERVAL_HOURS).hours.do(scheduled_tracking_job)

    # Also run once immediately
    logger.info("Running initial tracking job...")
    scheduled_tracking_job()

    # Keep the scheduler running
    logger.info("Scheduler is now running. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == '__main__':
    run_scheduler()
