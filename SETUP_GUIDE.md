# Quick Setup Guide

This guide will help you get the Price Tracker running in under 5 minutes.

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Email (Gmail)

### Get Gmail App Password

1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification if not already enabled
4. Go to "App passwords"
5. Generate a new app password for "Mail"
6. Copy the 16-character password

### Configure .env File

```bash
cp .env.example .env
```

Edit `.env`:
```
EMAIL_SENDER=youremail@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_RECEIVER=where_to_send_alerts@gmail.com
```

## Step 3: Add Products to Track

Edit `config.py` and update `PRODUCTS_TO_TRACK`:

```python
PRODUCTS_TO_TRACK = [
    {
        'name': 'Your Product Name',
        'urls': {
            'amazon': 'https://www.amazon.com/dp/PRODUCTID',
            'bestbuy': 'https://www.bestbuy.com/site/product/SKU.p'
        },
        'target_price': 299.99  # Optional
    }
]
```

### How to Get Product URLs

**Amazon:**
- Go to product page
- Copy URL (should look like: amazon.com/dp/B0XXXXXX)

**Best Buy:**
- Go to product page
- Copy URL (should look like: bestbuy.com/site/.../XXXXXXX.p)

## Step 4: Test Run

```bash
# Track prices once
python price_tracker.py --track --summary

# Generate demo data to see how it works
python demo.py
```

## Step 5: View Results

After running the tracker:
- Check `logs/price_tracker.log` for activity
- View charts in `data/outputs/`
- Check your email for any alerts

## Step 6: Automate (Optional)

To run automatically every 12 hours:

```bash
python scheduler.py
```

Leave this running in the background and you'll get automatic price alerts!

## Troubleshooting

### "No module named 'X'"
```bash
pip install -r requirements.txt
```

### Email not sending
- Double-check you're using App Password, not regular password
- Make sure 2FA is enabled on Gmail
- Check spam folder

### Can't scrape Amazon/Best Buy
- Sites may be blocking requests temporarily
- Try again in a few hours
- Check your internet connection

### Charts not generating
```bash
pip install matplotlib seaborn pandas
```

## Need Help?

Check the main [README.md](README.md) for detailed documentation.
