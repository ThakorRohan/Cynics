import re
from asyncio import create_subprocess_exec
from asyncio import sleep

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup

from Cynics import Cynics_IMG
from Cynics import setbot
from Cynics.__main__ import restart_all
from Cynics.utils.dynamic_filt import dynamic_data_filter


try:
    repo = Repo()
except InvalidGitRepositoryError:
    pass


@setbot.on_callback_query(dynamic_data_filter('change_branches'))
async def chng_branch(_, query):
    buttons = [
        [InlineKeyboardButton(r, callback_data=f'chng_branch_{r}')]
        for r in repo.branches
    ]
    if Cynics_IMG:
        await query.message.edit_caption(
            'Which Branch would you like to change to?\n' +
            '(this might break your userbot' +
            'if you are not cautious of what you are doing)',
        ),
        await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    else:
        await query.message.edit(
            'Which Branch would you like to change to?',
            reply_markup=InlineKeyboardMarkup(buttons),
        )


async def branch_button_callback(_, __, query):
    if re.match(r'chng_branch_', query.data):
        return True


branch_button_create = filters.create(branch_button_callback)


@setbot.on_callback_query(branch_button_create)
async def change_to_branch(client, query):
    branch_match = re.findall(r'master|dev|translations', query.data)
    if branch_match:
        try:
            repo.git.checkout(branch_match[0])
        except GitCommandError as exc:
            await query.message.edit(f'**ERROR**: {exc}')
            return
        await create_subprocess_exec(
            'pip3',
            'install',
            '-U',
            '-r',
            'requirements.txt',
        )
        await query.message.edit(
            'Branch Changed to {}\nplease consider checking the logs'.format(
                repo.active_branch,
            ),
        )
        await query.answer()
        await sleep(60)
        await restart_all()
    else:
        await query.answer('Doesnt look like an Official Branch, Aborting!')
