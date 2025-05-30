from telegram import Update, Bot
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
import os

# Çevre değişkenlerinden token ve chat id al
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Kullanıcı bazlı filtre tutucu
user_filters = {}

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funding Rate Bot'a hoşgeldiniz! \n\nKomutlar:\n/filter BTC ETH\n/premium")

# /filter komutu: Kullanıcıya ait filtreleri saklar
async def filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    filters = context.args
    user_filters[user_id] = filters
    await update.message.reply_text(f"Filtreniz kaydedildi: {', '.join(filters)}")

# /premium komutu: Premium duyurusu yapar
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "✨ Premium Üye Olun! \n"
        "Funding Fee alarm eşiklerini, coin filtrelerini ve anlık uyarıları kişiselleştirin. \n\n"
        "✉️ Katılmak için: https://t.me/+premium_kanal_linki"
    )
    await update.message.reply_text(msg)

# Ana fonksiyon
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("filter", filter_handler))
    app.add_handler(CommandHandler("premium", premium))

    print("🚀 Bot başlatıldı...")
    app.run_polling()
