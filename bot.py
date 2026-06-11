import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

load_dotenv()

from modules.username_search import search_username
from modules.phone_search import search_phone
from modules.email_search import search_email
from modules.telegram_parser import get_telegram_user_info

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск по username", callback_data="search_username")],
        [InlineKeyboardButton("📞 Поиск по номеру", callback_data="search_phone")],
        [InlineKeyboardButton("✉️ Поиск по email", callback_data="search_email")],
        [InlineKeyboardButton("📱 Telegram user", callback_data="telegram_user")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    await update.message.reply_text(
        "🔍 *OSINT Бот*\n\n"
        "Бот собирает информацию из открытых источников.\n\n"
        "Выберите тип поиска:",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == "search_username":
        await query.edit_message_text(
            "🔍 *Поиск по username*\n\nОтправьте username: @username или просто username",
            parse_mode="Markdown"
        )
        context.user_data['search_type'] = 'username'
    elif action == "search_phone":
        await query.edit_message_text(
            "📞 *Поиск по номеру*\n\nОтправьте номер: +380XXXXXXXXX",
            parse_mode="Markdown"
        )
        context.user_data['search_type'] = 'phone'
    elif action == "search_email":
        await query.edit_message_text(
            "✉️ *Поиск по email*\n\nОтправьте email: example@mail.com",
            parse_mode="Markdown"
        )
        context.user_data['search_type'] = 'email'
    elif action == "telegram_user":
        await query.edit_message_text(
            "📱 *Telegram user*\n\nОтправьте username или ID: @username или 123456789",
            parse_mode="Markdown"
        )
        context.user_data['search_type'] = 'telegram'
    elif action == "help":
        await query.edit_message_text(
            "ℹ️ *Помощь*\n\n"
            "🔍 username — проверка на 700+ сайтах\n"
            "📞 номер — информация о номере\n"
            "✉️ email — проверка утечек\n"
            "📱 Telegram — данные из Telegram\n\n"
            "Все данные из открытых источников.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    search_type = context.user_data.get('search_type')
    query_text = update.message.text.strip()
    
    if not search_type:
        await update.message.reply_text("Сначала выберите тип поиска через /start", reply_markup=get_main_keyboard())
        return
    
    status_msg = await update.message.reply_text(f"🔍 Поиск: `{query_text}`...", parse_mode="Markdown")
    
    try:
        if search_type == 'username':
            results = await search_username(query_text)
        elif search_type == 'phone':
            results = await search_phone(query_text)
        elif search_type == 'email':
            results = await search_email(query_text)
        elif search_type == 'telegram':
            results = await get_telegram_user_info(query_text)
        else:
            results = ["❌ Неизвестный тип поиска"]
        
        if not results:
            results = ["❌ Ничего не найдено"]
        
        response = f"✅ *Результаты* (`{query_text}`)\n\n"
        for result in results[:20]:
            response += f"• {result}\n"
            if len(response) > 3800:
                await update.message.reply_text(response, parse_mode="Markdown")
                response = ""
        
        if response:
            await update.message.reply_text(response, parse_mode="Markdown")
        
        await update.message.reply_text("🔍 Что дальше?", reply_markup=get_main_keyboard())
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:200]}")
    finally:
        await status_msg.delete()
        context.user_data['search_type'] = None

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['search_type'] = None
    await update.message.reply_text("❌ Поиск отменен. /start", reply_markup=get_main_keyboard())

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}")

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден!")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()