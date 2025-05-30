import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate?limit=100"
BYBIT_URL = "https://api.bybit.com/v2/public/funding/prev-funding-rate"
OKX_URL = "https://www.okx.com/api/v5/public/funding-rate?instType=SWAP"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print("Telegram response:", response.text)

def process_funding(symbol, rate):
    emoji = "🟢"
    if abs(rate) >= 1.5:
        emoji = "🔴"
    elif abs(rate) >= 1.0:
        emoji = "🟠"
    return f"{emoji} {symbol} funding rate: {rate:.2f}%"

def fetch_binance():
    try:
        r = requests.get(BINANCE_URL).json()
        for item in r:
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.5:
                msg = process_funding(item["symbol"], rate)
                send_telegram_message(msg)
    except Exception as e:
        send_telegram_message(f"Binance Error: {e}")

def fetch_bybit():
    try:
        r = requests.get(BYBIT_URL).json()
        for item in r.get("result", []):
            rate = float(item["funding_rate"]) * 100
            if abs(rate) >= 0.5:
                msg = process_funding(item["symbol"], rate)
                send_telegram_message(msg)
    except Exception as e:
        send_telegram_message(f"Bybit Error: {e}")

def fetch_okx():
    try:
        r = requests.get(OKX_URL).json()
        for item in r.get("data", []):
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.5:
                msg = process_funding(item["instId"], rate)
                send_telegram_message(msg)
    except Exception as e:
        send_telegram_message(f"OKX Error: {e}")

def main():
    print("✅ Script started")
    fetch_binance()
    fetch_bybit()
    fetch_okx()
    print("✅ All checks complete")

if __name__ == "__main__":
    main()
