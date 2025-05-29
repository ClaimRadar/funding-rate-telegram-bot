import os
import requests
from datetime import datetime

# Telegram bot bilgileri ortam değişkenlerinden alınır
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate?limit=100"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print("Telegram response:", response.json())

def fetch_binance():
    try:
        r = requests.get(BINANCE_URL).json()
        alerts = []
        for item in r:
            symbol = item["symbol"]
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.0:
                color = "🟢"
                if abs(rate) >= 1.5:
                    color = "🔴"
                elif abs(rate) >= 1.0:
                    color = "🟠"
                alerts.append(f"{color} {symbol} funding rate: {rate:.2f}%")
        return alerts
    except Exception as e:
        return [f"❌ Binance fetch error: {e}"]

def main():
    print("✅ Script started")
    try:
        message_lines = fetch_binance()
        print(f"✅ Alerts found: {len(message_lines)}")
        if message_lines:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            print("📬 Sending message to Telegram...")
            send_telegram_message(f"📊 Funding Rate Alerts ({now}):\n" + "\n".join(message_lines))
        else:
            print("ℹ️ No alerts to send.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    main()
