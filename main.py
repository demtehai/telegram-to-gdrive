import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Логирование
logging.basicConfig(level=logging.INFO)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_FOLDER = os.getenv("GDRIVE_FOLDER")

# Telegram
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Google Drive сервис
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'service_account.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# Загрузка файла
def upload_to_drive(filepath, filename):
    file_metadata = {
        'name': filename,
        'parents': [GDRIVE_FOLDER]
    }
    media = MediaFileUpload(filepath, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata, media_body=media, fields='id, webViewLink'
    ).execute()
    return uploaded_file.get('webViewLink')

@dp.message_handler(content_types=['photo', 'video'])
async def handle_media(msg: Message):
    file_id = msg.photo[-1].file_id if msg.photo else msg.video.file_id
    tg_file = await bot.get_file(file_id)
    file_path = tg_file.file_path

    filename = f"{file_id}.jpg" if msg.photo else f"{file_id}.mp4"
    local_path = f"temp/{filename}"
    os.makedirs("temp", exist_ok=True)

    await bot.download_file(file_path, destination=local_path)

    try:
        link = upload_to_drive(local_path, filename)
        await msg.reply(f"✅ Загружено в Google Drive:\n{link}")
    finally:
        os.remove(local_path)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
