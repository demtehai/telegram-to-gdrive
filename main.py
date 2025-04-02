# main.py
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Logging
logging.basicConfig(level=logging.INFO)

# Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_FOLDER = os.getenv("GDRIVE_FOLDER")

# Bot init
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Google Drive Auth
ga = GoogleAuth()
ga.LocalWebserverAuth()
drive = GoogleDrive(ga)

def upload_file_to_gdrive(file_path, file_name):
    file = drive.CreateFile({'title': file_name, 'parents': [{'id': GDRIVE_FOLDER}]})
    file.SetContentFile(file_path)
    file.Upload()
    return file['alternateLink']

@dp.message_handler(content_types=['photo', 'video'])
async def handle_media(msg: Message):
    file_id = msg.photo[-1].file_id if msg.photo else msg.video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    file_name = f"{file_id}.jpg" if msg.photo else f"{file_id}.mp4"
    local_path = f"temp/{file_name}"
    os.makedirs("temp", exist_ok=True)
    await bot.download_file(file_path, destination=local_path)

    link = upload_file_to_gdrive(local_path, file_name)
    os.remove(local_path)

    await msg.reply(f"✅ Загружено в Google Drive: {link}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
