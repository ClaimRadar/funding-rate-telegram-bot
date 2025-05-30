import requests
from datetime import datetime
import os
from filters_and_ui import load_user_data  # 👈 yeni eklendi

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate?limit=100"

def send_telegram_message(message, user_chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": user_chat_id, "text": message}
    requests.post(url, data=data)

def fetch_binance(user_id, tracked_coins):
    try:
        r = requests.get(BINANCE_URL).json()
        alerts = []
        for item in r:
            symbol = item["symbol"]
            if symbol not in tracked_coins:
                continue  # ⛔ sadece kullanıcının izlediği coin'ler
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
    print("✅ Script started")

    # 🔄 Tüm kullanıcıları al
    user_data = load_user_data()
    if not user_data:
        print("No users found.")
        return

    for user_id, tracked_coins in user_data.items():
        alerts = fetch_binance(user_id, tracked_coins)
        if alerts:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            msg = f"📊 Funding Rate Alerts ({now}):\n" + "\n".join(alerts)
            send_telegram_message(msg, user_id)
            print(f"✅ Sent to {user_id}: {len(alerts)} alerts")
        else:
            print(f"ℹ️ No alerts for {user_id}")

if __name__ == "__main__":
    main()
