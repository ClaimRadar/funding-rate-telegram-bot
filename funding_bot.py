import requests
import time
from datetime import datetime, timezone
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate?limit=100"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    print("✅ Telegram response:", response.text)

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
                alerts.append({
                    "symbol": symbol,
                    "rate": rate,
                    "color": color
                })
        return alerts
    except Exception as e:
        print("❌ Binance fetch error:", e)
        return []

def main():
    print("🚀 Script started")
    alerts = fetch_binance()
    print(f"📈 Alerts found: {len(alerts)}")
    
    for alert in alerts:
        symbol = alert["symbol"]
        rate = alert["rate"]
        color = alert["color"]
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        message = (
            f"{color} *{symbol}* funding rate alert!\n"
            f"Rate: `{rate:.2f}%`\n"
            f"Time: {now}"
        )
        send_telegram_message(message)
        time.sleep(1)  # Telegram rate limit protection

if __name__ == "__main__":
    main()
