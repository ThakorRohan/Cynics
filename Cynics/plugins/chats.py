import os

from pyrogram import filters

from Cynics import AdminSettings
from Cynics import app
from Cynics import COMMAND_PREFIXES
from Cynics import DB_AVAILABLE
from Cynics import edit_or_reply
from Cynics.utils import capture_err

if DB_AVAILABLE:
    from Cynics.plugins.database.chats_db import update_chat, get_all_chats

MESSAGE_RECOUNTER = 0

__MODULE__ = 'Chats'
__HELP__ = """
──「 **Export Chatlist** 」──
-> `chatlist`
Send a list of chats you are in to your saved messages.
"""


def get_msgc():
    return MESSAGE_RECOUNTER


@app.on_message(filters.group, group=10)
async def updatemychats(_, message):
    global MESSAGE_RECOUNTER
    if DB_AVAILABLE:
        update_chat(message.chat)
    MESSAGE_RECOUNTER += 1


@app.on_message(
    filters.user(AdminSettings) & filters.command(
        'chatlist', COMMAND_PREFIXES,
    ),
)
@capture_err
async def get_chat(client, message):
    if not DB_AVAILABLE:
        await edit_or_reply(message, text="You haven't set up a database!")
        return
    all_chats = get_all_chats()
    chatfile = 'List of chats.\n'
    for chat in all_chats:
        if str(chat.chat_username) != 'None':
            chatfile += '{} - ({}): @{}\n'.format(
                chat.chat_name, chat.chat_id, chat.chat_username,
            )
        else:
            chatfile += f'{chat.chat_name} - ({chat.chat_id})\n'

    with open('Cynics/cache/chatlist.txt', 'w', encoding='utf-8') as writing:
        writing.write(str(chatfile))
        writing.close()

    await client.send_document(
        'self',
        document='Cynics/cache/chatlist.txt',
        caption='Here is a list of chats in my database.',
    )
    await edit_or_reply(
        message,
        text='Sent to saved messages.',
    )
    os.remove('Cynics/cache/chatlist.txt')
