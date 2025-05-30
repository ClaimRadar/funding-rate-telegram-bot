from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import os

USER_DATA_FILE = "user_data.json"
PREMIUM_LINK = "https://t.me/joinchat/premium-link"

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to the Funding Rate Bot!\nUse /addcoin BTCUSDT to start tracking coins.")

async def addcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    coin = " ".join(context.args).upper()
    if not coin:
        await update.message.reply_text("❌ Please specify a coin symbol. Example: /addcoin PEPEUSDT")
        return
    data = load_user_data()
    data.setdefault(user_id, [])
    if coin not in data[user_id]:
        data[user_id].append(coin)
        save_user_data(data)
        await update.message.reply_text(f"✅ {coin} has been added to your list.")
    else:
        await update.message.reply_text(f"ℹ️ {coin} is already in your list.")

async def removecoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    coin = " ".join(context.args).upper()
    data = load_user_data()
    if user_id in data and coin in data[user_id]:
        data[user_id].remove(coin)
        save_user_data(data)
        await update.message.reply_text(f"🗑️ {coin} has been removed from your list.")
    e
