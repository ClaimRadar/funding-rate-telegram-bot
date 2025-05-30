import requests
import time
from datetime import datetime, timedelta, timezone
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate?limit=100"
BYBIT_URL = "https://api.bybit.com/v5/market/funding/prev-funding-rate?category=linear"
BITGET_URL = "https://api.bitget.com/api/mix/v1/market/funding-rate?productType=umcbl"
DERIBIT_URL = "https://www.deribit.com/api/v2/public/get_funding_chart_data?instrument_name=BTC-PERPETUAL&start_timestamp=0"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    print("✅ Telegram response:", response.text)

def get_next_funding_time():
    now = datetime.now(timezone.utc)
    next_hour = ((now.hour // 8) + 1) * 8 % 24
    next_funding = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
    if next_funding <= now:
        next_funding += timedelta(hours=8)
    delta = next_funding - now
    return f"in {delta.seconds // 3600}h {delta.seconds % 3600 // 60}m"

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
                alerts.append({"symbol": symbol, "rate": rate, "color": color, "exchange": "Binance"})
        return alerts
    except Exception as e:
        print("❌ Binance fetch error:", e)
        return []

def fetch_bybit():
    try:
        r = requests.get(BYBIT_URL).json()
        items = r.get("result", {}).get("list", [])
        alerts = []
        for item in items:
            symbol = item["symbol"]
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.5:
                color = "🟢"
                if abs(rate) >= 1.5:
                    color = "🔴"
                elif abs(rate) >= 1.0:
                    color = "🟠"
                alerts.append({"symbol": symbol, "rate": rate, "color": color, "exchange": "Bybit"})
        return alerts
    except Exception as e:
        print("❌ Bybit fetch error:", e)
        return []

def fetch_bitget():
    try:
        r = requests.get(BITGET_URL).json()
        items = r.get("data", [])
        alerts = []
        for item in items:
            symbol = item["symbol"]
            rate = float(item["fundingRate"])*100
            if abs(rate) >= 0.5:
                color = "🟢"
                if abs(rate) >= 1.5:
                    color = "🔴"
                elif abs(rate) >= 1.0:
                    color = "🟠"
                alerts.append({"symbol": symbol, "rate": rate, "color": color, "exchange": "Bitget"})
        return alerts
    except Exception as e:
        print("❌ Bitget fetch error:", e)
        return []

def fetch_deribit():
    try:
        r = requests.get(DERIBIT_URL).json()
        entries = r.get("result", {}).get("data", [])
        if entries:
            rate = entries[-1][1]*100
            if abs(rate) >= 0.5:
                color = "🟢"
                if abs(rate) >= 1.5:
                    color = "🔴"
                elif abs(rate) >= 1.0:
                    color = "🟠"
                return [{"symbol": "BTC-PERP", "rate": rate, "color": color, "exchange": "Deribit"}]
        return []
    except Exception as e:
        print("❌ Deribit fetch error:", e)
        return []

def main():
    print("🚀 Script started")
    alerts = fetch_binance() + fetch_bybit() + fetch_bitget() + fetch_deribit()
    print(f"📈 Total alerts found: {len(alerts)}")

    funding_time = get_next_funding_time()

    for alert in alerts:
        symbol = alert["symbol"]
        rate = alert["rate"]
        color = alert["color"]
        exchange = alert["exchange"]
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        message = (
            f"{color} *{symbol}* ({exchange}) funding rate alert!\n"
            f"Rate: `{rate:.2f}%`\n"
            f"Time: {now}\n"
            f"Next Funding: {funding_time}"
        )
        send_telegram_message(message)
        time.sleep(1)

if __name__ == "__main__":
    main()
