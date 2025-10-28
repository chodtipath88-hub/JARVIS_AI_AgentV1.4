from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from brain import Brain
from finance_manager import FinanceManager
from news_manager import NewsManager

# ใส่ token ของคุณตรงนี้
TOKEN = "8466815685:AAEaWdioW8UMo6ly_18Om7CHmf09aCjwnA8"
NEWS_API_KEY = "a11de2d46a164d5dbd43282d93a33260"

# เรียกใช้โมดูลหลัก
jarvis = Brain()
finance = FinanceManager()
news = NewsManager(api_key=NEWS_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("สวัสดีครับ ผมคือ JARVIS 🤖\nพิมพ์ 'รายรับ', 'รายจ่าย', 'สรุป', หรือ 'ข่าววันนี้' ได้เลย!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.message.from_user.first_name or "user"

    # --- ระบบรายรับ ---
    if text.startswith("รายรับ"):
        parts = text.split()
        if len(parts) >= 3:
            desc = parts[1]
            try:
                amt = float(parts[2])
                resp = finance.add_transaction(user, "income", desc, amt)
            except:
                resp = "⚠️ ตัวอย่าง: รายรับ เงินเดือน 10000"
        else:
            resp = "⚠️ ใช้รูปแบบ: รายรับ รายการ จำนวน"
        await update.message.reply_text(resp)
        return

    # --- ระบบรายจ่าย ---
    if text.startswith("รายจ่าย"):
        parts = text.split()
        if len(parts) >= 3:
            desc = parts[1]
            try:
                amt = float(parts[2])
                resp = finance.add_transaction(user, "expense", desc, amt)
            except:
                resp = "⚠️ ตัวอย่าง: รายจ่าย ค่าอาหาร 200"
        else:
            resp = "⚠️ ใช้รูปแบบ: รายจ่าย รายการ จำนวน"
        await update.message.reply_text(resp)
        return

    # --- สรุปยอด ---
    if text.startswith("สรุป"):
        resp = finance.get_summary(user)
        await update.message.reply_text(resp)
        return

    # --- ข่าวประจำวัน ---
    if text.startswith("ข่าว"):
        headlines = news.fetch_top_headlines()
        if headlines:
            msg = "📰 ข่าววันนี้:\n\n" + "\n\n".join(headlines)
        else:
            msg = "ไม่สามารถดึงข่าวได้ในขณะนี้"
        await update.message.reply_text(msg)
        return

    # --- ถ้าไม่เข้าหมวดไหนเลย ให้ Jarvis คิดเอง ---
    resp = jarvis.think(text)
    await update.message.reply_text(resp)

def main():
    print("🚀 กำลังเชื่อมต่อ Telegram Bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Jarvis Telegram Bot พร้อมใช้งานแล้ว!")
    app.run_polling()

if __name__ == "__main__":
    main()
