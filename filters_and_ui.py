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
    # ... daha önce yazdığımız binance kodu ...

def fetch_okx(user_id, tracked_coins):
    try:
        r = requests.get("https://www.okx.com/api/v5/public/funding-rate").json()
        alerts = []
        for item in r["data"]:
            symbol = item["instId"].replace("-", "")
            if symbol not in tracked_coins:
                continue
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.5:
                color = "🟢"
                if abs(rate) >= 1.5:
                    color = "🔴"
                elif abs(rate) >= 1.0:
                    color = "🟠"
                alerts.append(f"{color} OKX - {symbol} funding rate: {rate:.2f}%")
        return alerts
    except Exception as e:
        return [f"OKX fetch error: {e}"]

def fetch_bybit(user_id, tracked_coins):
    try:
        r = requests.get("https://api.bybit.com/v2/public/funding/prev-funding-rate").json()
        alerts = []
        for item in r["result"]:
            symbol = item["symbol"]
            if symbol not in tracked_coins:
                continue
            rate = float(item["funding_rate"]) * 100
            if abs(rate) >= 0.5:
                color = "🟢"
                if abs(rate) >= 1.5:
                    color = "🔴"
                elif abs(rate) >= 1.0:
                    color = "🟠"
                alerts.append(f"{color} Bybit - {symbol} funding rate: {rate:.2f}%")
        return alerts
    except Exception as e:
        return [f"Bybit fetch error: {e}"]


def main():
    print("✅ Script started")

    user_data = load_user_data()
    if not user_data:
        print("No users found.")
        return

    for user_id, tracked_coins in user_data.items():
        messages = []

        messages += fetch_binance(user_id, tracked_coins)
        messages += fetch_okx(user_id, tracked_coins)
        messages += fetch_bybit(user_id, tracked_coins)

        if messages:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            msg = f"📊 Funding Rate Alerts ({now}):\n" + "\n".join(messages)
            send_telegram_message(msg, user_id)
            print(f"✅ Sent to {user_id}: {len(messages)} alerts")
        else:
            print(f"ℹ️ No alerts for {user_id}")


if __name__ == "__main__":
    main()
