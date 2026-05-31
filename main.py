import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import time

TOKEN = "8514009693:AAEEdrOEV_8F8FpRsBT6fYWdlBMHenCcMjk"
ADMIN_ID = 8758830915
CHANNEL = "@Burmese_Anime"

bot = telebot.TeleBot(TOKEN)

user_data = {}
DB_FILE = "posts_db.json"

# ----------------- DB FUNCTIONS -----------------

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_post_to_db(post):
    db = load_db()
    db.append(post)
    save_db(db)

# ----------------- BOT HANDLERS -----------------

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "📸 Send Photo")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    if message.from_user.id != ADMIN_ID:
        return
    user_data.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "❌ Cancelled")

# ----------------- PHOTO STEP -----------------

@bot.message_handler(content_types=['photo'])
def photo(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "photo": message.photo[-1].file_id
    }

    bot.send_message(message.chat.id, "✍️ Send Message")

# ----------------- TEXT STEPS -----------------

@bot.message_handler(content_types=['text'])
def text(message):
    if message.from_user.id != ADMIN_ID:
        return

    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    data = user_data[chat_id]

    # STEP 1: caption text
    if "text" not in data:
        data["text"] = message.text
        bot.send_message(chat_id, "🔗 Send Link")
        return

    # STEP 2: link + finalize post
    if "link" not in data:
        data["link"] = message.text

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("ကြည့်ရန်", url=data["link"])
        )

        post_data = {
            "photo": data["photo"],
            "text": data["text"],
            "link": data["link"],
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # SAVE TO DB
        add_post_to_db(post_data)

        # ADMIN PREVIEW ONLY
        bot.send_photo(
            chat_id,
            data["photo"],
            caption=data["text"],
            reply_markup=markup
        )

        user_data.pop(chat_id, None)

print("Bot Running...")
bot.infinity_polling()
