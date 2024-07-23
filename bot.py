import json
import os
import time
import asyncio
import aiohttp
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
    async with aiohttp.request(method='GET',
                               url=f'https://fond-pangolin-lately.ngrok-free.app/botapi/check_registered/{message.from_user.id}') as status_req:
        status = await status_req.json()
    if status['registered'] == '0':
        data = {'usr': message.from_user.username, 'name': message.from_user.first_name,
                'last': message.from_user.last_name}
        headers = {'Content-Type': 'application/json'}
        for k in list(data.keys()):
            if not data[k]:
                data[k] = 'n/a'
        data = json.dumps(data)
        async with aiohttp.request(method='GET',
                                   url=f'https://fond-pangolin-lately.ngrok-free.app/botapi/register_user/{message.from_user.id}',
                                   data=data,
                                   headers=headers) as register_req:
            register = await register_req.json()
        if not register['message'] == 'success':
            print('registration error!')
    keyboard_set = [[types.InlineKeyboardButton(text='Тапать!',
                                                web_app=types.WebAppInfo(
                                                    url='https://fivtee8.github.io/PavelKombat/'))]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_set)
    async with aiohttp.request(method='GET', url=
    f'https://fond-pangolin-lately.ngrok-free.app/botapi/set_await_query_id/{message.from_user.id}/{os.getenv("botkey")}') as set_await:
        set_await_json = await set_await.json()
    if set_await_json['code'] == '0':
        sent = await message.answer(
            "Начни тапать Павла Сергеевича! \n Данное сообщение будет удалено через 15 секунд для предотвращения атак.",
            reply_markup=keyboard)
        await asyncio.sleep(15)
        await bot.delete_message(sent.chat.id, sent.message_id)
        await bot.delete_message(message.chat.id, message.message_id)
        await aiohttp.request(method='GET',
                              url=f'https://fond-pangolin-lately.ngrok-free.app/botapi/unawait_query/{message.from_user.id}')
    else:
        await message.answer('Ошибка' + set_await_json['code'])


'''
@dp.callback_query(F.data == 'lets_go')
async def handle_query(callback: types.CallbackQuery):
    await callback.answer()
'''


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
