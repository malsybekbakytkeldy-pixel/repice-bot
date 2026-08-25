import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from openai import OpenAI
from aiohttp import web

TELEGRAM_TOKEN = "8510266775:AAGk_1vdhRwAlff5PmAT0_pU5vfTqXUxQRw"
GROQ_API_KEY = "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" 

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        f"Сәлем, {message.from_user.first_name}! 🤖🍳\n"
        "Мен серверде жұмыс істейтін ақылды аспаз-ботпын. Маған кез келген тағамды жаз!"
    )

@dp.message()
async def get_recipe(message: types.Message):
    user_text = message.text
    wait_msg = await message.answer("⏳ Рецепт дайындалып жатыр, күте тұрыңыз...")

    try:
        prompt = f"Сен тәжірибелі шеф-аспазсың. Мына тағамның рецептін қазақ тілінде, түсінікті етіп, ингредиенттерімен және дайындалу жолымен толық жазып бер: {user_text}"
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Сен қазақ тілінде жауап беретін көмекшісің."},
                {"role": "user", "content": prompt}
            ]
        )
        
        recipe_text = response.choices[0].message.content
        
        await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)
        await message.answer(recipe_text)
        
    except Exception as e:
        # aiogram бойынша дұрыс жауап беру тәсілі
        await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)
        await message.answer(f"❌ Қате орын алды: {e}")

# Render порт талабын орындауға арналған веб-сервер
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

async def web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

async def main():
    print("Бот серверде іске қосылды!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(web_server())
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
