
import requests
import time
from datetime import datetime
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate?limit=100"
BYBIT_URL = "https://api.bybit.com/v2/public/funding/prev-funding-rate"
OKX_URL = "https://www.okx.com/api/v5/public/funding-rate"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def fetch_binance():
    try:
        r = requests.get(BINANCE_URL).json()
        alerts = []
        for item in r:
            symbol = item["symbol"]
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.5:
                color = "🟢"
                if abs(rate) >= 1.5:
                    color = "🔴"
                elif abs(rate) >= 1.0:
                    color = "🟠"
                alerts.append(f"{color} {symbol} funding rate: {rate:.2f}%")
        return alerts
    except Exception as e:
        return [f"Binance fetch error: {e}"]

def main():
    message_lines = []
    message_lines.extend(fetch_binance())
    if message_lines:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        send_telegram_message(f"📊 Funding Rate Alerts ({now}):\n" + "\n".join(message_lines))

if __name__ == "__main__":
    main()
