import asyncio

from pyrogram import Client
from configparser import ConfigParser
from configparser import NoOptionError
from configparser import NoSectionError

config = ConfigParser()
try:
    config.read('config.ini')
    API_ID = config.getint('Cynics', 'api_id')
    API_HASH = config.get('Cynics', 'api_hash')
except (NoOptionError, NoSectionError):
    API_ID = int(input('enter Telegram APP ID: '))
    API_HASH = input('enter Telegram API HASH: ')


async def main(api_id, api_hash):
    """generate StringSession for the current MemorySession"""
    async with Client(':memory:', api_id=api_id, api_hash=api_hash) as app:
        await app.send_message(
            "me", f"#STRING_SESSION\n\n```{await app.export_session_string()}```"
        )
        print("Done !, session string has been sent to saved messages!")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(API_ID, API_HASH))
