import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8514009693:AAEEdrOEV_8F8FpRsBT6fYWdlBMHenCcMjk"
ADMIN_ID = 8758830915
CHANNEL = "@Burmese_Anime"

bot = telebot.TeleBot(TOKEN)

user_data = {}


# ---------------- START ----------------

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "📤 Send Photo, Video or GIF"
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
def receive_photo(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "type": "photo",
        "file_id": message.photo[-1].file_id
    }

    bot.send_message(message.chat.id, "✍️ Send Caption")


# ---------------- VIDEO ----------------

@bot.message_handler(content_types=['video'])
def receive_video(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "type": "video",
        "file_id": message.video.file_id
    }

    bot.send_message(message.chat.id, "✍️ Send Caption")


# ---------------- GIF ----------------

@bot.message_handler(content_types=['animation'])
def receive_gif(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "type": "gif",
        "file_id": message.animation.file_id
    }

    bot.send_message(message.chat.id, "✍️ Send Caption")


# ---------------- TEXT ----------------

@bot.message_handler(content_types=['text'])
def receive_text(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text.startswith("/"):
        return

    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    data = user_data[chat_id]

    # Save caption
    if "caption" not in data:
        data["caption"] = message.text
        bot.send_message(chat_id, "🔗 Send Button Link")
        return

    # Save link and post
    if "link" not in data:
        data["link"] = message.text

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "ကြည့်ရန်",
                url=data["link"]
            )
        )

        try:
            # ---------- Preview ----------
            if data["type"] == "photo":
                bot.send_photo(
                    chat_id,
                    data["file_id"],
                    caption=data["caption"],
                    reply_markup=markup
                )

            elif data["type"] == "video":
                bot.send_video(
                    chat_id,
                    data["file_id"],
                    caption=data["caption"],
                    reply_markup=markup
                )

            elif data["type"] == "gif":
                bot.send_animation(
                    chat_id,
                    data["file_id"],
                    caption=data["caption"],
                    reply_markup=markup
                )

            # ---------- Post To Channel ----------
            if data["type"] == "photo":
                bot.send_photo(
                    CHANNEL,
                    data["file_id"],
                    caption=data["caption"],
                    reply_markup=markup
                )

            elif data["type"] == "video":
                bot.send_video(
                    CHANNEL,
                    data["file_id"],
                    caption=data["caption"],
                    reply_markup=markup
                )

            elif data["type"] == "gif":
                bot.send_animation(
                    CHANNEL,
                    data["file_id"],
                    caption=data["caption"],
                    reply_markup=markup
                )

            bot.send_message(
                chat_id,
                "✅ Successfully Posted To Channel"
            )

        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error:\n{e}"
            )

        user_data.pop(chat_id, None)


print("🤖 Bot Running...")

bot.infinity_polling(
    skip_pending=True,
    timeout=60,
    long_polling_timeout=60
)
