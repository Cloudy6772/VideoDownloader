import os
import time
import telebot
from pytubefix import YouTube
import instaloader
import shutil

TOKEN = "7626812897:AAHSgw_7DO9JJpxYvlWQW8UHyKx0BH1np_U"
bot = telebot.TeleBot(TOKEN)

TEMP_DIR = "temp_download"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Киньте ссылку на Ютуб или Инстаграм видео")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if not text.startswith("http"):
        bot.send_message(chat_id, "Пожалуйста, киньте правильную ссылку")
        return

    bot.send_message(chat_id, "Загружается...")

    try:
        file_path = None

        if "youtube.com" in text or "youtu.be" in text:
            yt = YouTube(text)
            stream = yt.streams.get_highest_resolution()
            file_path = stream.download(output_path=TEMP_DIR)

        elif "instagram.com" in text:
            loader = instaloader.Instaloader(dirname_pattern=TEMP_DIR, save_metadata=False, download_comments=False)
            shortcode = text.split("/")[-2]
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target="insta_temp")
            folder_path = os.path.join(TEMP_DIR, "insta_temp")
            files = [f for f in os.listdir(folder_path) if f.endswith((".mp4", ".jpg"))]
            if files:
                file_path = os.path.join(folder_path, files[0])
            else:
                bot.send_message(chat_id, "Не нашлось никакое видео.")
                return
        else:
            bot.send_message(chat_id, "Может принимать только YouTube или Instagram ссылку.")
            return

        with open(file_path, 'rb') as f:
            if file_path.endswith(".mp4"):
                bot.send_video(chat_id, f)
            elif file_path.endswith(".jpg"):
                bot.send_photo(chat_id, f)

        # Удаляем файл и временную папку
        if os.path.exists(file_path):
            os.remove(file_path)
        if "insta_temp" in file_path:
            shutil.rmtree(os.path.join(TEMP_DIR, "insta_temp"), ignore_errors=True)

    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка:\n{e}")

print("Бот запущен!")
bot.infinity_polling()
