import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from openai import OpenAI
from aiohttp import web


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN табылмады!")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY табылмады!")


client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        f"Сәлем, {message.from_user.first_name}! 🤖🍳\n"
        "Мен ақылды аспаз-ботпын. Маған кез келген тағамды жаз!"
    )


@dp.message(F.text)
async def get_recipe(message: types.Message):

    user_text = message.text

    wait_msg = await message.answer(
        "⏳ Рецепт дайындалып жатыр..."
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Сен қазақ тілінде жауап беретін "
                        "тәжірибелі аспазсың."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Мына тағамның рецептін қазақ тілінде жаз. "
                        "Ингредиенттерін және дайындалу жолын "
                        "қадамдармен түсіндір:\n\n"
                        f"{user_text}"
                    )
                }
            ]
        )

        recipe_text = response.choices[0].message.content

        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )

        await message.answer(recipe_text)

    except Exception as e:

        print("ERROR:", e)

        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )

        await message.answer(
            "❌ Қате орын алды. Сервер журналын тексеріңіз."
        )


async def handle(request):
    return web.Response(text="Bot is running!")


app = web.Application()
app.router.add_get("/", handle)


async def web_server():

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()


async def main():

    await web_server()

    print("Бот серверде іске қосылды!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
