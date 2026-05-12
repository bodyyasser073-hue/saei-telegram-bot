
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from openai import OpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

DATA_FILE = "users.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = str(update.effective_user.id)

    if uid not in users:
        users[uid] = {
            "name": update.effective_user.first_name,
            "streak": 0,
            "tasks": [],
            "joined": str(datetime.now())
        }
        save_users(users)

    text = (
        "🚀 أهلاً بك في SAEI Bot\n\n"
        "الأوامر:\n"
        "/plan - خطة مذاكرة\n"
        "/tasks - المهام\n"
        "/addtask - إضافة مهمة\n"
        "/streak - الستريك\n"
        "/pomodoro - مؤقت\n"
        "/ai - ذكاء اصطناعي\n"
    )

    await update.message.reply_text(text)

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📚 خطة اليوم:\n"
        "1. رياضيات - 90 دقيقة\n"
        "2. فيزياء - 60 دقيقة\n"
        "3. مراجعة - 30 دقيقة\n"
        "4. Pomodoro × 4"
    )
    await update.message.reply_text(msg)

async def addtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()

    task = " ".join(context.args)

    if not task:
        await update.message.reply_text("❌ اكتب المهمة بعد الأمر")
        return

    users[uid]["tasks"].append(task)
    save_users(users)

    await update.message.reply_text(f"✅ تمت إضافة المهمة: {task}")

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()

    user_tasks = users[uid]["tasks"]

    if not user_tasks:
        await update.message.reply_text("📭 لا توجد مهام")
        return

    text = "📝 مهامك:\n\n"
    for i, t in enumerate(user_tasks, start=1):
        text += f"{i}. {t}\n"

    await update.message.reply_text(text)

async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()

    streak_count = users[uid]["streak"]

    await update.message.reply_text(
        f"🔥 الستريك الحالي: {streak_count} يوم"
    )

async def pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏳ Pomodoro بدأ: 25 دقيقة تركيز"
    )

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text("❌ اكتب سؤالك")
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an Arabic study assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        return

    message = " ".join(context.args)

    users = load_users()

    sent = 0

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=message)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"📣 تم الإرسال إلى {sent}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("/"):
        return

    await update.message.reply_text(
        "🧠 استخدم /ai للسؤال بالذكاء الاصطناعي"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(CommandHandler("tasks", tasks))
    app.add_handler(CommandHandler("addtask", addtask))
    app.add_handler(CommandHandler("streak", streak))
    app.add_handler(CommandHandler("pomodoro", pomodoro))
    app.add_handler(CommandHandler("ai", ai))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("🚀 SAEI Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
