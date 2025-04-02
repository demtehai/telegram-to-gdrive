import os
import asyncio
import logging
from threading import Thread
from flask import Flask

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Настройка логов ---
logging.basicConfig(level=logging.INFO)

# --- Flask сервер ---
app = Flask(__name__)

@app.route("/ping")
def ping():
    return "OK", 200

def run_flask():
    app.run(host="0.0.0.0", port=8000)

# --- Настройки окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_FOLDER = os.getenv("GDRIVE_FOLDER")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# --- Авторизация в Google Drive ---
import json
credentials_info = json.loads(GOOGLE_CREDENTIALS)
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# --- Telegram Bot ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def upload_to_gdrive(file_name: str, local_path: str):
    file_metadata = {"name": file_name, "parents": [GDRIVE_FOLDER]}
    media = MediaFileUpload(local_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="webViewLink"
    ).execute()
    return file["webViewLink"]

@dp.message(lambda msg: msg.content_type in ("photo", "video"))
async def handle_media(msg: Message):
    file_id = msg.photo[-1].file_id if msg.photo else msg.video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_name = f"{file_id}.jpg" if msg.photo else f"{file_id}.mp4"
    local_path = f"temp/{file_name}"

    os.makedirs("temp", exist_ok=True)
    await bot.download_file(file_path, destination=local_path)

    link = upload_to_gdrive(file_name, local_path)
    os.remove(local_path)

    await msg.reply(f"✅ Загружено в Google Drive:\n{link}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(main())
