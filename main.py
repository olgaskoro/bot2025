import os
import openai
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_PATH = "/webhook"
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL") or "https://твой-домен.onrender.com"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

client = openai.OpenAI(api_key=OPENAI_API_KEY)

PSYCHOLOGIST_PROMPT = """
You are a professional psychologist with many years of experience:: 
Your job is to provide friendly, supportive, and meaningful responses:: 
You use cognitive behavioral therapy (CBT) and active listening techniques::
Answer calmly, respectfully and with care for the client:: Form answers that are short and complete in meaning, 
avoid interruptions mid-sentence, keep the meaning within 500 tokens:: Answer in Russian.
"""

async def ask_chatgpt(user_message: str) -> str:
    try:
        response = client.chat.completions.create(
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
async def start(message: types.Message):
    await message.answer("Привет! Я психолог-бот. Задай мне вопрос, и я помогу тебе 😊")

@dp.message()
async def handle_message(message: Message):
    user_text = message.text.strip()
    logging.info(f"Получено сообщение: {user_text}")  # <— добавили лог
    try:
        response = await ask_chatgpt(user_text)
        logging.info(f"Ответ от OpenAI: {response}")  # <— добавили лог
        await message.answer(response)
    except Exception as e:
        logging.error(f"Ошибка в handle_message: {e}")
        await message.answer("Произошла ошибка. Попробуй ещё раз позже 🙏")


async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    main()
