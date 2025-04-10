import os
import openai
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# Загружаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота с новыми параметрами
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Инициализация клиента OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Описание роли бота
PSYCHOLOGIST_PROMPT = """
You are a professional psychologist with many years of experience:: 
Your job is to provide friendly, supportive, and meaningful responses:: 
You use cognitive behavioral therapy (CBT) and active listening techniques::
Answer calmly, respectfully and with care for the client:: Form answers that are short and complete in meaning, 
avoid interruptions mid-sentence, keep the meaning within 500 tokens:: Answer in Russian.
"""

async def ask_chatgpt(user_message: str) -> str:
    """Отправляет запрос в ChatGPT и возвращает ответ."""
    try:
        response = client.chat.completions.create(  # Новый способ вызова OpenAI API
            model="gpt-4",
            messages=[
                {"role": "system", "content": PSYCHOLOGIST_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка запроса к OpenAI: {e}")
        return "Извините, произошла ошибка. Попробуйте позже."

@dp.message(Command("start"))
async def start(message: Message):
    """Обрабатывает команду /start"""
    await message.answer(
        "Привет! Я психолог-бот. Задай мне вопрос, и я помогу тебе разобраться в себе 😊"
    )

@dp.message()
async def handle_message(message: Message):
    """Обрабатывает сообщения пользователей и отвечает с помощью ChatGPT."""
    user_text = message.text.strip()
    response = await ask_chatgpt(user_text)
    await message.answer(response)

async def main():
    """Запуск бота в асинхронном режиме."""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
