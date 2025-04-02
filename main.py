import os
import logging
import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from google.oauth2 import service_account
from googleapiclient.discovery import build
from aiohttp import ClientSession

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_FOLDER = os.getenv("GDRIVE_FOLDER")

# Настройка бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Чтение переменной окружения с ключом сервисного аккаунта
google_credentials = os.getenv("GOOGLE_CREDENTIALS")  # Получаем строку из переменной окружения
credentials_info = json.loads(google_credentials)  # Преобразуем строку обратно в объект JSON
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Google Drive сервис
drive_service = build("drive", "v3", credentials=credentials)

# Функция загрузки файла на Google Drive
def upload_to_gdrive(filename, file_path):
    file_metadata = {
        "name": filename,
        "parents": [GDRIVE_FOLDER],
    }
    media_body = open(file_path, "rb")
    uploaded_file = (
        drive_service.files()
        .create(body=file_metadata, media_body=media_body, fields="id,webViewLink")
        .execute()
    )
    return uploaded_file.get("webViewLink")

# Обработчик медиа
@dp.message(F.content_type.in_(['photo', 'video']))
async def handle_media(message: Message):
    file = message.photo[-1] if message.photo else message.video
    file_info = await bot.get_file(file.file_id)

    file_name = f"{file.file_id}.jpg" if message.photo else f"{file.file_id}.mp4"
    local_path = f"temp/{file_name}"
    os.makedirs("temp", exist_ok=True)

    # Скачивание
    await bot.download_file(file_info.file_path, destination=local_path)

    # Загрузка в Google Drive
    link = upload_to_gdrive(file_name, local_path)

    # Удаление временного файла
    os.remove(local_path)

    # Ответ пользователю
    await message.answer(f"✅ Загружено: {link}")

# Старт бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
