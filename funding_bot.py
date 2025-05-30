import requests
import time
from datetime import datetime, timedelta, timezone
import os
import json
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USER_DATA_FILE = "user_data.json"

BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate?limit=100"
BYBIT_URL = "https://api.bybit.com/v5/market/funding/prev-funding-rate?category=linear"
BITGET_URL = "https://api.bitget.com/api/mix/v1/market/funding-rate?productType=umcbl"
DERIBIT_URL = "https://www.deribit.com/api/v2/public/get_funding_chart_data?instrument_name=BTC-PERPETUAL&start_timestamp=0"

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def get_next_funding_time():
    now = datetime.now(timezone.utc)
    next_hour = ((now.hour // 8) + 1) * 8 % 24
    next_funding = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
    if next_funding <= now:
        next_funding += timedelta(hours=8)
    delta = next_funding - now
    return f"in {delta.seconds // 3600}h {delta.seconds % 3600 // 60}m"

def fetch_all_funding():
    alerts = []
    try:
        r = requests.get(BINANCE_URL).json()
        for item in r:
            symbol = item["symbol"]
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.5:
                color = "🟢" if abs(rate) < 1.0 else "🟠" if abs(rate) < 1.5 else "🔴"
                alerts.append({"symbol": symbol, "rate": rate, "color": color, "exchange": "Binance"})
    except: pass
    try:
        r = requests.get(BYBIT_URL).json().get("result", {}).get("list", [])
        for item in r:
            symbol = item["symbol"]
            rate = float(item["fundingRate"]) * 100
            if abs(rate) >= 0.5:
                color = "🟢" if abs(rate) < 1.0 else "🟠" if abs(rate) < 1.5 else "🔴"
                alerts.append({"symbol": symbol, "rate": rate, "color": color, "exchange": "Bybit"})
    except: pass
    try:
        r = requests.get(BITGET_URL).json().get("data", [])
        for item in r:
            symbol = item["symbol"]
            rate = float(item["fundingRate"])*100
            if abs(rate) >= 0.5:
                color = "🟢" if abs(rate) < 1.0 else "🟠" if abs(rate) < 1.5 else "🔴"
                alerts.append({"symbol": symbol, "rate": rate, "color": color, "exchange": "Bitget"})
    except: pass
    try:
        r = requests.get(DERIBIT_URL).json().get("result", {}).get("data", [])
        if r:
            rate = r[-1][1]*100
            if abs(rate) >= 0.5:
                color = "🟢" if abs(rate) < 1.0 else "🟠" if abs(rate) < 1.5 else "🔴"
                alerts.append({"symbol": "BTC-PERP", "rate": rate, "color": color, "exchange": "Deribit"})
    except: pass
    return alerts

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Funding Radar Bot!\n\nUse /addcoin <SYMBOL> to watch a coin.\nUse /listcoins to see your watchlist.\nUse /joinpremium to unlock more features.")

async def addcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    symbol = context.args[0].upper() if context.args else None
    if not symbol:
        return await update.message.reply_text("❗ Usage: /addcoin SYMBOL")
    data = load_user_data()
    data.setdefault(user_id, {"coins": [], "premium": False})
    if symbol not in data[user_id]["coins"]:
        data[user_id]["coins"].append(symbol)
        save_user_data(data)
    await update.message.reply_text(f"✅ {symbol} added to your watchlist!")

async def listcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_user_data()
    coins = data.get(user_id, {}).get("coins", [])
    if coins:
        await update.message.reply_text("👀 Your watchlist:\n" + "\n".join(coins))
    else:
        await update.message.reply_text("ℹ️ You haven't added any coins yet.")

async def removecoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    symbol = context.args[0].upper() if context.args else None
    if not symbol:
        return await update.message.reply_text("❗ Usage: /removecoin SYMBOL")
    data = load_user_data()
    if user_id in data and symbol in data[user_id]["coins"]:
        data[user_id]["coins"].remove(symbol)
        save_user_data(data)
        await update.message.reply_text(f"✅ {symbol} removed from your watchlist.")
    else:
        await update.message.reply_text("❌ Symbol not found in your watchlist.")

async def joinpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💎 Become a Premium Member:\nJoin here: https://t.me/YourChannelName")

def alert_users():
    data = load_user_data()
    funding_data = fetch_all_funding()
    funding_time = get_next_funding_time()
    for user_id, info in data.items():
        coins = info.get("coins", [])
        for item in funding_data:
            if item["symbol"] in coins:
                msg = f"{item['color']} *{item['symbol']}* ({item['exchange']})\nFunding Rate: `{item['rate']:.2f}%`\nNext funding {funding_time}"
                send_telegram_message(msg, chat_id=user_id)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addcoin", addcoin))
    app.add_handler(CommandHandler("listcoins", listcoins))
    app.add_handler(CommandHandler("removecoin", removecoin))
    app.add_handler(CommandHandler("joinpremium", joinpremium))
    app.run_polling()

if __name__ == "__main__":
    main()
