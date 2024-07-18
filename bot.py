import os
import telebot
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

# now we have them as a handy python strings!
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    button = telebot.types.InlineKeyboardButton('Тапать!', web_app=telebot.types.WebAppInfo('https://fivtee8.github.io/pombat/'))
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(button)

    # button = telebot.types.KeyboardButton(text="Тапать!", web_app=telebot.types.WebAppInfo('https://fivtee8.github.io/pombat/'))
    # keyboard = telebot.types.ReplyKeyboardMarkup()
    # keyboard.add(button)

    bot.send_message(message.chat.id, text="Начни тапать Павла Сергеевича!", reply_markup=keyboard)

    #bot.reply_to(message, "text", reply_markup=keyboard)

"""
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'start':
        print("YES!") """


if __name__ == '__main__':
    bot.infinity_polling()