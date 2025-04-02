import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(message: Message):
    await message.reply("Бот работает!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
