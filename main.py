import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8514009693:AAEEdrOEV_8F8FpRsBT6fYWdlBMHenCcMjk"
ADMIN_ID = 8758830915

bot = telebot.TeleBot(TOKEN)

user_data = {}

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

@bot.message_handler(content_types=['photo'])
def photo(message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.chat.id] = {
        "photo": message.photo[-1].file_id
    }

    bot.send_message(message.chat.id, "✍️ Send Message")

@bot.message_handler(content_types=['text'])
def text(message):
    if message.from_user.id != ADMIN_ID:
        return

    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    data = user_data[chat_id]

    if "text" not in data:
        data["text"] = message.text
        bot.send_message(chat_id, "🔗 Send Link")
        return

    if "link" not in data:
        data["link"] = message.text

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("ကြည့်ရန်", url=data["link"])
        )

        bot.send_photo(
            chat_id,
            data["photo"],
            caption=data["text"],
            reply_markup=markup
        )

        user_data.pop(chat_id, None)

print("Bot Running...")
bot.infinity_polling()
    user_data[message.chat.id] = {
        "photo": message.photo[-1].file_id
    }

    bot.send_message(message.chat.id, "✍️ Send Message Text")

# ---------------- TEXT FLOW ----------------
@bot.message_handler(content_types=['text'])
def process(message):
    if message.from_user.id != ADMIN_ID:
        return

    chat_id = message.chat.id

    if chat_id not in user_data:
        return

    data = user_data[chat_id]

    # STEP 1: MESSAGE
    if "text" not in data:
        data["text"] = message.text
        bot.send_message(chat_id, "🔗 Send Link")
        return

    # STEP 2: LINK → PREVIEW
    if "link" not in data:
        data["link"] = message.text

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("ကြည့်ရန်", url=data["link"])
        )

        bot.send_photo(
            chat_id,
            data["photo"],
            caption=f"📌 PREVIEW\n\n{data['text']}",
            reply_markup=markup
        )

        bot.send_message(chat_id, "👀 Preview Ready (Not Sent to Channel)")

        user_data.pop(chat_id, None)

print("Bot is running...")
bot.infinity_polling()
