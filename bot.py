import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

# now we have them as a handy python strings!
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard_set = [[types.InlineKeyboardButton(text='Тапать!',
                                                web_app=types.WebAppInfo(url='https://fivtee8.github.io/PavelKombat/'))]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_set)
    await message.answer("Начни тапать Павла Сергеевича!", reply_markup=keyboard)


'''
@dp.callback_query(F.data == 'lets_go')
async def handle_query(callback: types.CallbackQuery):
    await callback.message.edit_text('Приложение открыто. Удачи!')
    await callback.answer()
'''


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
