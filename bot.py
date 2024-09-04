import json
import os
import asyncio

import aiogram.dispatcher.event.bases
import aiohttp
from typing import Dict, Any
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import decode_payload, create_start_link


if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv()

# now we have them as a handy python strings!
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def check_subbed(message: types.message):
    channel_id = os.getenv('channel_id')

    try:
        if type((await bot.get_chat_member(channel_id, message.from_user.id))) in [aiogram.types.chat_member_administrator.ChatMemberAdministrator, aiogram.types.chat_member_owner.ChatMemberOwner, aiogram.types.chat_member_member.ChatMemberMember]:
            return True
        else:
            return False

    except Exception as e:
        print(e)
        return False


async def ensure_regged(message: types.Message):
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
            return False

    return True


@dp.update.outer_middleware
async def middleware(handler, event: types.Update, data: Dict[str, Any]):
    message = event.message or event.callback_query.message

    if not await ensure_regged(message):
        raise aiogram.dispatcher.event.bases.CancelHandler()

    if message and message.text.startswith('/'):
        if not (await check_subbed(message)):
            repped = await message.reply('Подпишись, падла!\n\n@pdevkprff')

            await asyncio.sleep(15)
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.delete_message(repped.chat.id, repped.message_id)

            raise aiogram.dispatcher.event.bases.CancelHandler()
        else:
            return await handler(event, data)


@dp.message(aiogram.filters.Command('myref'))
async def myref(message: types.Message):
    async with aiohttp.request(method='GET',
                               url=f'https://fond-pangolin-lately.ngrok-free.app/botapi/fetchref/{message.from_user.id}') as status_req:
        status = (await status_req.json())['ref']

    text = f'{status}\n\n{await create_start_link(bot, status, encode=True)}'

    sent = await message.answer(text)

    await asyncio.sleep(15)
    await bot.delete_message(sent.chat.id, sent.message_id)
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message(aiogram.filters.Command('ref'))
async def ref(message: types.Message, code=None, ignore_del=False):
    ref_code = message.text.split()[1]

    if code is not None:
        ref_code = code

    async with aiohttp.request(method='GET',
                               url=f'https://fond-pangolin-lately.ngrok-free.app/botapi/doref/{message.from_user.id}/{ref_code}') as status_req:
        status = (await status_req.json())['message']

    text = ''
    if status == 'denied':
        text = 'Вы уже использовали реферальный код!'
    elif status == 'invalid':
        text = 'Такого кода не существует...'
    else:
        text = 'Успешно! Вам зачисленно 1000 ПавелПоинтов'

    sent = await message.answer(text)

    if ignore_del:
        return sent, message, status

    if status == 'ok':
        await asyncio.sleep(2*60*60)
    else:
        await asyncio.sleep(15)

    await bot.delete_message(sent.chat.id, sent.message_id)
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message(CommandStart(deep_link=True))
async def start_with_ref(message: types.Message, command: CommandObject):
    payload = decode_payload(command.args)
    sent, oldmess, status = await ref(message, code=payload, ignore_del=True)

    await start_handler(message)
    await bot.delete_message(oldmess.chat.id, oldmess.message_id)
    if status == 'ok':
        await asyncio.sleep(4*60*60 - 15)
    await bot.delete_message(sent.chat.id, sent.message_id)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
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
        async with aiohttp.request(method='GET',
                              url=f'https://fond-pangolin-lately.ngrok-free.app/botapi/unawait_query/{message.from_user.id}') as resp:
            pass
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
