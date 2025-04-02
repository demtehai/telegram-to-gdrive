import os
import logging
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_FOLDER = os.getenv("GDRIVE_FOLDER")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

credentials = service_account.Credentials.from_service_account_info(GOOGLE_CREDENTIALS)
drive_service = build('drive', 'v3', credentials=credentials)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def upload_to_gdrive(file_name, file_path):
    file_metadata = {
        'name': file_name,
        'parents': [GDRIVE_FOLDER]
    }

    media = MediaFileUpload(file_path, resumable=True)

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return f"https://drive.google.com/file/d/{uploaded_file.get('id')}/view?usp=drive_link"

@dp.message(lambda message: message.photo or message.video)
async def handle_media(msg: types.Message):
    if msg.photo:
        file_id = msg.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        file_name = f"{file_id}.jpg"
    else:
        file_id = msg.video.file_id
        file_info = await bot.get_file(file_id)
        file_name = f"{file_id}.mp4"

    file_path = file_info.file_path
    local_path = f"/tmp/{file_name}"

    os.makedirs("/tmp", exist_ok=True)
    await bot.download_file(file_path, destination=local_path)

    link = upload_to_gdrive(file_name, local_path)
    os.remove(local_path)

    await msg.reply(f"✅ Загружено в Google Drive: {link}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
