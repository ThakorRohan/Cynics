import asyncio
from time import time

from coffeehouse.api import API
from coffeehouse.exception import CoffeeHouseError as CFError
from coffeehouse.lydia import LydiaAI
from pyrogram import filters

import Cynics.plugins.database.lydia_db as sql
from Cynics import AdminSettings
from Cynics import app
from Cynics import COMMAND_PREFIXES
from Cynics import edit_or_reply
from Cynics import LYDIA_API
from Cynics import Owner
from Cynics import OwnerUsername
from Cynics import setbot

__MODULE__ = 'Chatbot'
__HELP__ = """
An AI Powered Chat Bot Module

──「 **Chatbot** 」──
-> `addchat`
Enables AI on chat.

-> `rmchat`
Removes AI on chat.

Powered by CoffeeHouse API created by @Intellivoid.
"""

CoffeeHouseAPI = API(LYDIA_API)
api_ = LydiaAI(CoffeeHouseAPI)


@app.on_message(
    filters.user(AdminSettings) &
    filters.command('addchat', COMMAND_PREFIXES),
)
async def add_chat(_, message):
    global api_
    chat_id = message.chat.id
    is_chat = sql.is_chat(chat_id)
    if not is_chat:
        ses = api_.create_session()
        ses_id = str(ses.id)
        expires = str(ses.expires)
        sql.set_ses(chat_id, ses_id, expires)
        await edit_or_reply(
            message,
            text='`AI successfully enabled for this chat!`',
        )
    else:
        await edit_or_reply(
            message,
            text='`AI is already enabled for this chat!`',
        )

    await asyncio.sleep(5)
    await message.delete()


@app.on_message(
    filters.user(AdminSettings) &
    filters.command('rmchat', COMMAND_PREFIXES),
)
async def remove_chat(_, message):
    chat_id = message.chat.id
    is_chat = sql.is_chat(chat_id)
    if not is_chat:
        await edit_or_reply(
            message,
            text="`AI isn't enabled here in the first place!`",
        )
    else:
        sql.rem_chat(chat_id)
        await edit_or_reply(message, text='`AI disabled successfully!`')

    await asyncio.sleep(5)
    await message.delete()


@app.on_message(
    ~filters.user(AdminSettings) &
    ~filters.edited &
    (filters.group | filters.private),
    group=6,
)
async def chat_bot(client, message):
    global api_
    chat_id = message.chat.id
    is_chat = sql.is_chat(chat_id)
    if not is_chat:
        return
    if message.text and not message.document:
        if not await check_message(client, message):
            return
        sesh, exp = sql.get_ses(chat_id)
        query = message.text
        try:
            if int(exp) < time():
                ses = api_.create_session()
                ses_id = str(ses.id)
                expires = str(ses.expires)
                sql.set_ses(chat_id, ses_id, expires)
                sesh, exp = sql.get_ses(chat_id)
        except ValueError:
            pass
        try:
            await client.send_chat_action(chat_id, action='typing')
            rep = api_.think_thought(sesh, query)
            await asyncio.sleep(0.3)
            await message.reply_text(rep)
        except CFError as e:
            await setbot.send_message(
                Owner, f'Chatbot error: {e} occurred in {chat_id}!',
            )


async def check_message(_, message):
    if message.chat.type == 'private':
        return True
    if message.text.lower() == f'@{OwnerUsername}':
        return True
    if message.reply_to_message:
        return message.reply_to_message.from_user.id == Owner
