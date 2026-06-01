import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import shutil
from datetime import datetime

# ---------------- CONFIG ----------------

TOKEN = "8514009693:AAEEdrOEV_8F8FpRsBT6fYWdlBMHenCcMjk"
ADMIN_ID = 8758830915
CHANNEL = "@Burmese_Anime"

DB_FILE = "posts.json"
BACKUP_FILE = "backup_posts.json"

bot = telebot.TeleBot(TOKEN)

user_data = {}
restore_wait = set()

# ---------------- DATABASE ----------------

def load_posts():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

def add_post(post):
    posts = load_posts()
    posts.append(post)
    save_posts(posts)
    create_backup()

def create_backup():
    try:
        if os.path.exists(DB_FILE):
            shutil.copy(DB_FILE, BACKUP_FILE)
    except:
        pass

# ---------------- START ----------------

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "📸 Send Photo\n\nCommands:\n/cancel /stats /backup /restore /deletepost"
    )

# ---------------- CANCEL ----------------

@bot.message_handler(commands=['cancel'])
def cancel(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data.pop(message.chat.id, None)

    bot.send_message(message.chat.id, "❌ Cancelled")

# ---------------- PHOTO ----------------

@bot.message_handler(content_types=['photo'])
def photo(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "photo": message.photo[-1].file_id
    }

    bot.send_message(message.chat.id, "✍️ Send Caption")

# ---------------- TEXT FLOW ----------------

@bot.message_handler(content_types=['text'])
def text(message):

    if message.from_user.id != ADMIN_ID:
        return

    if message.text.startswith("/"):
        return

    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    data = user_data[chat_id]

    # caption step
    if "text" not in data:
        data["text"] = message.text
        bot.send_message(chat_id, "🔗 Send Button Link")
        return

    # link step + post
    if "link" not in data:
        data["link"] = message.text

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("▶️ ကြည့်ရန်", url=data["link"])
        )

        # preview
        bot.send_photo(
            chat_id,
            data["photo"],
            caption=data["text"],
            reply_markup=markup
        )

        try:
            msg = bot.send_photo(
                CHANNEL,
                data["photo"],
                caption=data["text"],
                reply_markup=markup
            )

            post_data = {
                "message_id": msg.message_id,
                "photo": data["photo"],
                "caption": data["text"],
                "link": data["link"],
                "date": str(datetime.now())
            }

            add_post(post_data)

            bot.send_message(chat_id, "✅ Posted + Saved + Backup Created")

        except Exception as e:
            bot.send_message(chat_id, f"❌ Channel Error: {e}")

        user_data.pop(chat_id, None)

# ---------------- STATS ----------------

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return

    posts = load_posts()

    bot.send_message(
        message.chat.id,
        f"📊 Stats\n\n📝 Posts: {len(posts)}"
    )

# ---------------- BACKUP ----------------

@bot.message_handler(commands=['backup'])
def backup(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not os.path.exists(DB_FILE):
        bot.send_message(message.chat.id, "❌ No database found")
        return

    with open(DB_FILE, "rb") as f:
        bot.send_document(message.chat.id, f, caption="💾 Backup File")

# ---------------- RESTORE ----------------

@bot.message_handler(commands=['restore'])
def restore(message):
    if message.from_user.id != ADMIN_ID:
        return

    restore_wait.add(message.chat.id)

    bot.send_message(message.chat.id, "📤 Send JSON file")

@bot.message_handler(content_types=['document'])
def restore_file(message):

    if message.from_user.id != ADMIN_ID:
        return

    if message.chat.id not in restore_wait:
        return

    if not message.document.file_name.endswith(".json"):
        bot.send_message(message.chat.id, "❌ Only JSON allowed")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open(DB_FILE, "wb") as f:
        f.write(downloaded)

    restore_wait.remove(message.chat.id)

    bot.send_message(message.chat.id, "✅ Restored Successfully")

# ---------------- DELETE POST ----------------

@bot.message_handler(commands=['deletepost'])
def delete_post(message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) != 2:
        bot.send_message(message.chat.id, "/deletepost <index>")
        return

    try:
        idx = int(args[1])
        posts = load_posts()

        if idx < 0 or idx >= len(posts):
            bot.send_message(message.chat.id, "❌ Invalid index")
            return

        posts.pop(idx)
        save_posts(posts)

        bot.send_message(message.chat.id, "🗑 Deleted from database")

    except:
        bot.send_message(message.chat.id, "❌ Error")

# ---------------- RUN ----------------

print("Bot Running...")
bot.infinity_polling(skip_pending=True)
