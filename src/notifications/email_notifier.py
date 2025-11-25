import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications for price drops"""

    def __init__(self, sender_email: str, sender_password: str, receiver_email: str):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def send_price_drop_alert(self, drop_info: Dict) -> bool:
        """
        Send email alert for a price drop

        Args:
            drop_info: Dictionary containing price drop details

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"🔔 Price Drop Alert: {drop_info['product']}"

            # Create HTML email body
            html_body = self._create_price_drop_html(drop_info)

            # Create plain text version
            text_body = f"""
Price Drop Alert!

Product: {drop_info['product']}
Site: {drop_info['site']}

Previous Price: ${drop_info['previous_price']:.2f}
Current Price: ${drop_info['current_price']:.2f}

Savings: ${drop_info['amount_drop']:.2f} ({drop_info['percentage_drop']:.1f}% off)

Time: {drop_info['timestamp']}

Happy shopping! 🛒
            """

            return self._send_email(subject, html_body, text_body)

        except Exception as e:
            logger.error(f"Failed to send price drop alert: {str(e)}")
            return False

    def send_daily_summary(self, summary_data: List[Dict]) -> bool:
        """
        Send daily summary of all tracked prices

        Args:
            summary_data: List of dictionaries with product price info

        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = f"📊 Daily Price Summary - {datetime.now().strftime('%Y-%m-%d')}"

            # Create HTML email body
            html_body = self._create_summary_html(summary_data)

            # Create plain text version
            text_body = "Daily Price Summary\n\n"
            for item in summary_data:
                text_body += f"{item['product']} - {item['site']}: ${item['price']:.2f}\n"

            return self._send_email(subject, html_body, text_body)

        except Exception as e:
            logger.error(f"Failed to send daily summary: {str(e)}")
            return False

    def _send_email(self, subject: str, html_body: str, text_body: str) -> bool:
        """Send email using SMTP"""
        if not self.sender_email or not self.sender_password:
            logger.warning("Email credentials not configured. Skipping email send.")
            return False

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = self.receiver_email

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            message.attach(part1)
            message.attach(part2)

            # Send email using Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {self.receiver_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def _create_price_drop_html(self, drop_info: Dict) -> str:
        """Create HTML formatted email for price drop"""
        return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: white;
                        border-radius: 10px;
                        padding: 30px;
                        max-width: 600px;
                        margin: 0 auto;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 8px;
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .product-name {{
                        font-size: 24px;
                        font-weight: bold;
                        margin: 10px 0;
                    }}
                    .price-box {{
                        display: flex;
                        justify-content: space-around;
                        margin: 20px 0;
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                    }}
                    .price-item {{
                        text-align: center;
                    }}
                    .price-label {{
                        color: #6c757d;
                        font-size: 14px;
                        margin-bottom: 5px;
                    }}
                    .price-value {{
                        font-size: 28px;
                        font-weight: bold;
                    }}
                    .old-price {{
                        color: #dc3545;
                        text-decoration: line-through;
                    }}
                    .new-price {{
                        color: #28a745;
                    }}
                    .savings {{
                        background-color: #28a745;
                        color: white;
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .details {{
                        color: #6c757d;
                        font-size: 14px;
                        margin-top: 20px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔔 Price Drop Alert!</h1>
                        <div class="product-name">{drop_info['product']}</div>
                        <div>at {drop_info['site']}</div>
                    </div>

                    <div class="price-box">
                        <div class="price-item">
                            <div class="price-label">Was</div>
                            <div class="price-value old-price">${drop_info['previous_price']:.2f}</div>
                        </div>
                        <div class="price-item">
                            <div class="price-label">Now</div>
                            <div class="price-value new-price">${drop_info['current_price']:.2f}</div>
                        </div>
                    </div>

                    <div class="savings">
                        💰 Save ${drop_info['amount_drop']:.2f} ({drop_info['percentage_drop']:.1f}% OFF)
                    </div>

                    <div class="details">
                        <p><strong>Detected:</strong> {drop_info['timestamp']}</p>
                        <p style="margin-top: 20px; text-align: center;">
                            Don't miss this deal! Prices may change at any time.
                        </p>
                    </div>

                    <div class="footer">
                        <p>Price Tracker - Automated Price Monitoring</p>
                        <p>You're receiving this because you're tracking this product</p>
                    </div>
                </div>
            </body>
        </html>
        """

    def _create_summary_html(self, summary_data: List[Dict]) -> str:
        """Create HTML formatted email for daily summary"""
        rows = ""
        for item in summary_data:
            rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{item['product']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{item['site']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #dee2e6; font-weight: bold; color: #28a745;">
                    ${item['price']:.2f}
                </td>
            </tr>
            """

        return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: white;
                        border-radius: 10px;
                        padding: 30px;
                        max-width: 800px;
                        margin: 0 auto;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th {{
                        background-color: #667eea;
                        color: white;
                        padding: 15px;
                        text-align: left;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Daily Price Summary</h1>
                        <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                    </div>

                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Site</th>
                                <th>Current Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </div>
            </body>
        </html>
        """
