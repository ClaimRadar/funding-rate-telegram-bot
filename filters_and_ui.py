from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import os

USER_DATA_FILE = "user_data.json"
PREMIUM_LINK = "https://t.me/joinchat/premium-link"

# Kullanıcı verisini yükle/kaydet
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Komutlar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Funding Rate botuna hoş geldin!\n/addcoin BTCUSDT yazarak takip etmek istediğin coin'leri ekleyebilirsin.")

async def addcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    coin = " ".join(context.args).upper()
    if not coin:
        await update.message.reply_text("❌ Lütfen coin sembolünü girin. Örn: /addcoin PEPEUSDT")
        return
    data = load_user_data()
    data.setdefault(user_id, [])
    if coin not in data[user_id]:
        data[user_id].append(coin)
        save_user_data(data)
        await update.message.reply_text(f"✅ {coin} eklendi.")
    else:
        await update.message.reply_text(f"ℹ️ {coin} zaten listenizde var.")

async def removecoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    coin = " ".join(context.args).upper()
    data = load_user_data()
    if user_id in data and coin in data[user_id]:
        data[user_id].remove(coin)
        save_user_data(data)
        await update.message.reply_text(f"🗑️ {coin} kaldırıldı.")
    else:
        await update.message.reply_text(f"❌ {coin} bulunamadı.")

async def listcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_user_data()
    coins = data.get(user_id, [])
    if coins:
        await update.message.reply_text(f"📋 Takip ettiğiniz coin'ler:\n" + "\n".join(coins))
    else:
        await update.message.reply_text("📭 Henüz coin eklemediniz. /addcoin ile ekleyin.")

async def joinpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🚀 Premium özelliklere katılmak için buraya tıklayın:\n{PREMIUM_LINK}")

# Bot uygulaması çalıştırıcı
def run_bot():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addcoin", addcoin))
    app.add_handler(CommandHandler("removecoin", removecoin))
    app.add_handler(CommandHandler("listcoins", listcoins))
    app.add_handler(CommandHandler("joinpremium", joinpremium))

    print("🤖 Bot aktif")
    app.run_polling()
