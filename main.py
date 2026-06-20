import telebot
import threading
import time

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8514009693:AAEpzpGDbT1IbjQcYCmiMbYRSFR1CM6VBiY"
ADMIN_ID = 8758830915
CHANNEL = "@Burmese_Anime"

bot = telebot.TeleBot(TOKEN)

user_data = {}
post_queue = []

POST_DELAY = 300  # Default 5 Minutes


# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data.pop(message.chat.id, None)

    bot.send_message(
        message.chat.id,
        "📤 Send Photo, Video or GIF"
    )


# ================= CANCEL =================

@bot.message_handler(commands=['cancel'])
def cancel(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data.pop(message.chat.id, None)

    bot.send_message(
        message.chat.id,
        "❌ Cancelled"
    )


# ================= TIME =================

@bot.message_handler(commands=['time'])
def set_time(message):
    global POST_DELAY

    if message.from_user.id != ADMIN_ID:
        return

    try:
        delay = int(message.text.split()[1])

        if delay < 1:
            bot.reply_to(message, "❌ Invalid Time")
            return

        POST_DELAY = delay

        bot.reply_to(
            message,
            f"✅ Auto Post Delay Set To {POST_DELAY}s"
        )

    except:
        bot.reply_to(
            message,
            "Usage:\n/time 300"
        )


# ================= PHOTO =================

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "type": "photo",
        "file_id": message.photo[-1].file_id
    }

    bot.send_message(
        message.chat.id,
        "✍️ Send Caption"
    )


# ================= VIDEO =================

@bot.message_handler(content_types=['video'])
def receive_video(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "type": "video",
        "file_id": message.video.file_id
    }

    bot.send_message(
        message.chat.id,
        "✍️ Send Caption"
    )


# ================= GIF =================

@bot.message_handler(content_types=['animation'])
def receive_gif(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "type": "gif",
        "file_id": message.animation.file_id
    }

    bot.send_message(
        message.chat.id,
        "✍️ Send Caption"
    )


# ================= TEXT =================

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

    if "caption" not in data:
        data["caption"] = message.text

        bot.send_message(
            chat_id,
            "🔗 Send Button Link"
        )
        return

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
            # Preview
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

            # Add Queue
            post_queue.append({
                "type": data["type"],
                "file_id": data["file_id"],
                "caption": data["caption"],
                "link": data["link"]
            })

            bot.send_message(
                chat_id,
                f"✅ Added To Queue\n"
                f"📦 Queue: {len(post_queue)}\n"
                f"⏰ Delay: {POST_DELAY}s"
            )

        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error:\n{e}"
            )

        user_data.pop(chat_id, None)


# ================= AUTO SENDER =================

def auto_sender():
    global POST_DELAY

    while True:
        if post_queue:

            data = post_queue.pop(0)

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(
                    "ကြည့်ရန်",
                    url=data["link"]
                )
            )

            try:
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

                print("Posted Successfully")

            except Exception as e:
                print("Post Error:", e)

            time.sleep(POST_DELAY)

        else:
            time.sleep(5)


threading.Thread(
    target=auto_sender,
    daemon=True
).start()


print("🤖 Bot Running...")

bot.infinity_polling(
    skip_pending=True,
    timeout=60,
    long_polling_timeout=60
)
