import os
import random
import telebot

from dotenv import load_dotenv
from telebot import types

from music_data import music, artists


# Завантаження токена з файлу .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Перевірка наявності токена
if not TOKEN:
    raise ValueError("Токен не знайдено. Перевір файл .env")

# Створення бота
bot = telebot.TeleBot(TOKEN)

# Зберігання поточної дії кожного користувача
user_steps = {}


# Створення головного меню
def create_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row("🎲 Рекомендація", "🎸 За жанром")
    keyboard.row("🌙 За настроєм", "🎤 Про виконавця")
    keyboard.row("✨ Схожі виконавці")

    return keyboard


# Форматування інформації про пісню
def format_song(song):
    return (
        f"🎵 <b>{song['title']}</b>\n"
        f"🎤 Виконавець: {song['artist']}\n"
        f"🎸 Жанр: {song['genre']}\n"
        f"🌙 Настрій: {song['mood']}\n"
        f"💿 Альбом: {song['album']}"
    )


# Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    user_steps.pop(message.chat.id, None)

    bot.send_message(
        message.chat.id,
        "Привіт! 🎧\n\n"
        "Я Soundscape — твій музичний помічник.\n"
        "Допоможу знаходити нові пісні та виконавців "
        "відповідно до твоїх музичних уподобань.\n\n"
        "Обирай, що хочеш зробити!",
        reply_markup=create_menu()
    )


# Команда /help
@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📖 <b>Як користуватися Soundscape?</b>\n\n"
        "/start — відкрити головне меню\n"
        "/help — переглянути інструкцію\n"
        "/recommend — отримати випадкову пісню\n\n"
        "Також ти можеш користуватися кнопками меню:\n"
        "🎲 отримати рекомендацію\n"
        "🎸 знайти музику за жанром\n"
        "🌙 знайти музику за настроєм\n"
        "🎤 дізнатися про виконавця\n"
        "✨ знайти схожих виконавців",
        parse_mode="HTML"
    )


# Команда /recommend
@bot.message_handler(commands=["recommend"])
def recommend(message):
    song = random.choice(music)

    bot.send_message(
        message.chat.id,
        "Ось твоя випадкова рекомендація! 🎧\n\n"
        + format_song(song),
        parse_mode="HTML"
    )


# Обробка всіх текстових повідомлень
@bot.message_handler(content_types=["text"])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Якщо користувач обирає випадкову рекомендацію
    if text == "🎲 Рекомендація":
        song = random.choice(music)

        bot.send_message(
            chat_id,
            "Ось що я тобі рекомендую! 🎧\n\n"
            + format_song(song),
            parse_mode="HTML"
        )

    # Пошук музики за жанром
    elif text == "🎸 За жанром":
        user_steps[chat_id] = "genre"

        genres = sorted(set(song["genre"] for song in music))

        bot.send_message(
            chat_id,
            "Напиши жанр, який тебе цікавить:\n\n"
            + "\n".join(genres)
        )

    # Пошук музики за настроєм
    elif text == "🌙 За настроєм":
        user_steps[chat_id] = "mood"

        moods = sorted(set(song["mood"] for song in music))

        bot.send_message(
            chat_id,
            "Який у тебе зараз настрій?\n\n"
            + "\n".join(moods)
        )

    # Пошук інформації про виконавця
    elif text == "🎤 Про виконавця":
        user_steps[chat_id] = "artist"

        bot.send_message(
            chat_id,
            "Напиши назву виконавця або гурту."
        )

    # Пошук схожих виконавців
    elif text == "✨ Схожі виконавці":
        user_steps[chat_id] = "similar"

        bot.send_message(
            chat_id,
            "Напиши назву виконавця, який тобі подобається."
        )

    # Обробка відповідей користувача
    elif chat_id in user_steps:

        step = user_steps[chat_id]

        # Пошук за жанром
        if step == "genre":
            results = [
                song for song in music
                if song["genre"].lower() == text.lower()
            ]

            if results:
                answer = "🎸 Ось пісні цього жанру:\n\n"

                for song in results:
                    answer += format_song(song) + "\n\n"

                bot.send_message(
                    chat_id,
                    answer,
                    parse_mode="HTML"
                )
            else:
                bot.send_message(
                    chat_id,
                    "На жаль, такого жанру поки немає в моїй базі."
                )

        # Пошук за настроєм
        elif step == "mood":
            results = [
                song for song in music
                if song["mood"].lower() == text.lower()
            ]

            if results:
                answer = "🌙 Музика під твій настрій:\n\n"

                for song in results:
                    answer += format_song(song) + "\n\n"

                bot.send_message(
                    chat_id,
                    answer,
                    parse_mode="HTML"
                )
            else:
                bot.send_message(
                    chat_id,
                    "Не знайшов пісень для такого настрою."
                )

        # Пошук інформації про виконавця
        elif step == "artist":
            artist_info = artists.get(text.lower())

            if artist_info:
                bot.send_message(chat_id, artist_info)
            else:
                bot.send_message(
                    chat_id,
                    "Не знайшов цього виконавця у своїй базі."
                )

        # Пошук схожих виконавців за жанром
        elif step == "similar":
            artist_songs = [
                song for song in music
                if song["artist"].lower() == text.lower()
            ]

            if artist_songs:
                artist_genres = [
                    song["genre"] for song in artist_songs
                ]

                similar = [
                    song for song in music
                    if song["genre"] in artist_genres
                    and song["artist"].lower() != text.lower()
                ]

                if similar:
                    answer = "✨ Можливо, тобі сподобаються:\n\n"

                    for song in similar:
                        answer += (
                            f"🎤 {song['artist']} — {song['title']}\n"
                        )

                    bot.send_message(chat_id, answer)
                else:
                    bot.send_message(
                        chat_id,
                        "Поки не знайшов схожих виконавців."
                    )
            else:
                bot.send_message(
                    chat_id,
                    "Не знайшов цього виконавця у своїй базі."
                )

        # Завершення поточної дії
        user_steps.pop(chat_id, None)

    else:
        bot.send_message(
            chat_id,
            "Скористайся кнопками меню або введи /help."
        )


# Запуск бота
print("Soundscape запущено!")
bot.infinity_polling()
