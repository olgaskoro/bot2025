from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import asyncio
import datetime
import pytz

TOKEN = "925556553:AAE5gTUPQ_tHlWy6VG-BAc-TJTxXfA1dXII"

# Мотивационные фразы
MOTIVATIONS = [
    "⚽ Сегодня отличный день, чтобы стать сильнее!",
    "🏋️‍♂️ Двигайся! Даже 15 минут тренировки лучше, чем ничего!",
    "🏆 Ты уже на шаг ближе к своей цели. Не останавливайся!",
    "📊 Спорт = энергия. Вставай и сделай зарядку!",
    "🌟 Твой прогресс начинается там, где заканчиваются отговорки."
]

# Кнопки меню
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📚 Книги о спорте", callback_data='books')],
        [InlineKeyboardButton("📞 Контакты", callback_data='contacts')],
        [InlineKeyboardButton("🌊 Спортивная музыка", callback_data='music')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Автоматическая регистрация чата для рассылки
    context.chat_data["registered"] = True

    await update.message.reply_text(
        "🎽 Привет! Я твой спортивный мотивационный бот!\n"
        "Я буду присылать тебе мотивационные сообщения каждый день:\n"
        "⏰ В 10:00, 12:00, 16:00, 17:00 и 20:00 по МСК.\n\n"
        "А пока можешь выбрать кнопку ниже:",
        reply_markup=get_main_menu()
    )

# Обработка команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Чем могу помочь?\n"
        "Вот что я умею:\n"
        "- Присылать мотивационные сообщения в течение дня\n"
        "- Показывать книги о спорте\n"
        "- Давать контакты\n"
        "- Поделиться спортивной музыкой\n\n"
        "Нажми /start, чтобы начать!"
    )

# Ответы на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'books':
        text = "📖 Рекомендуем к прочтению:\n- 'Эссенциализм' Грег МакКеон\n- 'Сила привычки' Чарльз Дахигг\n- 'Больше чем тело' Лекси Кайт"
    elif query.data == 'contacts':
        text = "📞 Свяжись с нами:\nInstagram: @fitness_bot\nTelegram: @yourcoach\nEmail: fitbot@example.com"
    elif query.data == 'music':
        text = "🎵 Спортивный плейлист:\n- Eye of the Tiger\n- Can't Hold Us\n- Lose Yourself"
    else:
        text = "❓ Неизвестная команда."

    await query.edit_message_text(text, reply_markup=get_main_menu())

# Планировщик рассылки
async def scheduler(application):
    tz = pytz.timezone("Europe/Moscow")
    target_hours = [10, 12, 16, 17, 20]  # Добавлены 17 и 20
    sent_today = set()

    while True:
        now = datetime.datetime.now(tz)
        if now.hour in target_hours and now.hour not in sent_today:
            message = random.choice(MOTIVATIONS)
            for chat_id in application.chat_data:
                try:
                    await application.bot.send_message(chat_id=chat_id, text=message)
                except Exception as e:
                    print(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
            sent_today.add(now.hour)

        if now.hour == 0:
            sent_today.clear()
        await asyncio.sleep(60)

# Фоновый запуск планировщика
async def on_startup(app: Application):
    asyncio.create_task(scheduler(app))

# Запуск бота
def main():
    app = Application.builder().token(TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🎽 Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
