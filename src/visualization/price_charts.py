import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# Set style for better-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class PriceChartGenerator:
    """Generate visualizations for price trends"""

    def __init__(self, output_dir: str = 'data/outputs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_price_history(self, df: pd.DataFrame, product_name: str,
                          save_path: str = None) -> str:
        """
        Plot price history for a product across different sites

        Args:
            df: DataFrame with columns: timestamp, site, price
            product_name: Name of the product
            save_path: Optional custom save path

        Returns:
            Path to saved chart
        """
        if df.empty:
            logger.warning(f"No data to plot for {product_name}")
            return None

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot each site with different color
        sites = df['site'].unique()
        colors = sns.color_palette("husl", len(sites))

        for site, color in zip(sites, colors):
            site_data = df[df['site'] == site].sort_values('timestamp')
            ax.plot(site_data['timestamp'], site_data['price'],
                   marker='o', label=site, color=color,
                   linewidth=2, markersize=6)

        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Price History: {product_name}',
                    fontsize=16, fontweight='bold', pad=20)

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 10)))
        plt.xticks(rotation=45, ha='right')

        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')

        # Add legend
        ax.legend(loc='best', framealpha=0.9, fontsize=10)

        # Add price range annotation
        min_price = df['price'].min()
        max_price = df['price'].max()
        ax.text(0.02, 0.98, f'Price Range: ${min_price:.2f} - ${max_price:.2f}',
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Tight layout
        plt.tight_layout()

        # Save figure
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{product_name.replace(' ', '_')}_price_history_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Chart saved to {save_path}")
        return save_path

    def plot_price_comparison(self, df: pd.DataFrame, product_name: str,
                             save_path: str = None) -> str:
        """
        Create bar chart comparing current prices across sites

        Args:
            df: DataFrame with latest prices from each site
            product_name: Name of the product
            save_path: Optional custom save path

        Returns:
            Path to saved chart
        """
        if df.empty:
            logger.warning(f"No data to plot for {product_name}")
            return None

        # Get latest price from each site
        latest_prices = df.sort_values('timestamp').groupby('site').last().reset_index()

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create bar chart
        sites = latest_prices['site']
        prices = latest_prices['price']
        colors = sns.color_palette("Set2", len(sites))

        bars = ax.bar(sites, prices, color=colors, alpha=0.8, edgecolor='black')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.2f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Formatting
        ax.set_xlabel('Store', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Price Comparison: {product_name}',
                    fontsize=16, fontweight='bold', pad=20)

        # Highlight lowest price
        min_idx = prices.idxmin()
        bars[min_idx].set_color('green')
        bars[min_idx].set_alpha(1.0)

        # Add grid
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')

        # Tight layout
        plt.tight_layout()

        # Save figure
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{product_name.replace(' ', '_')}_comparison_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Comparison chart saved to {save_path}")
        return save_path

    def plot_savings_tracker(self, df: pd.DataFrame, product_name: str,
                            target_price: float = None, save_path: str = None) -> str:
        """
        Plot price history with target price line and savings area

        Args:
            df: DataFrame with price history
            product_name: Name of the product
            target_price: Optional target price to highlight
            save_path: Optional custom save path

        Returns:
            Path to saved chart
        """
        if df.empty:
            logger.warning(f"No data to plot for {product_name}")
            return None

        # Convert timestamp to datetime and sort
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Get lowest price from each timestamp across all sites
        min_prices = df.groupby('timestamp')['price'].min().reset_index()

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot minimum price line
        ax.plot(min_prices['timestamp'], min_prices['price'],
               marker='o', color='#2E86AB', linewidth=3,
               markersize=8, label='Best Price', zorder=3)

        # Add target price line if provided
        if target_price:
            ax.axhline(y=target_price, color='#A23B72', linestyle='--',
                      linewidth=2, label=f'Target Price: ${target_price:.2f}',
                      zorder=2)

            # Highlight when price is below target
            below_target = min_prices[min_prices['price'] <= target_price]
            if not below_target.empty:
                ax.scatter(below_target['timestamp'], below_target['price'],
                          color='green', s=150, marker='*',
                          label='Below Target!', zorder=4)

        # Fill area under curve
        ax.fill_between(min_prices['timestamp'], min_prices['price'],
                       alpha=0.3, color='#2E86AB')

        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Best Price Tracker: {product_name}',
                    fontsize=16, fontweight='bold', pad=20)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45, ha='right')

        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')

        # Add legend
        ax.legend(loc='best', framealpha=0.9, fontsize=10)

        # Add stats box
        current_price = min_prices.iloc[-1]['price']
        lowest_price = min_prices['price'].min()
        highest_price = min_prices['price'].max()

        stats_text = f'Current: ${current_price:.2f}\n'
        stats_text += f'Lowest: ${lowest_price:.2f}\n'
        stats_text += f'Highest: ${highest_price:.2f}'

        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

        # Tight layout
        plt.tight_layout()

        # Save figure
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{product_name.replace(' ', '_')}_savings_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Savings tracker chart saved to {save_path}")
        return save_path
