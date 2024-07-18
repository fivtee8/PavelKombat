import json
import os
import asyncio
import requests

from aiogram import Bot, Dispatcher, types
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

    status_req = requests.get(f'https://fond-pangolin-lately.ngrok-free.app/botapi/check_registered/{message.from_user.id}')

    if status_req.json()['registered'] == '0':
        data = {'usr': message.from_user.username, 'name': message.from_user.first_name, 'last': message.from_user.last_name}
        register_req = requests.post(f'https://fond-pangolin-lately.ngrok-free.app/botapi/register_user/{message.from_user.id}', data=data)

        if not (register_req.json()['message'] == 'success'):
            print('registration error!')

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
