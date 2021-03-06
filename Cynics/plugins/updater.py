import os
import shutil
import sys

from git import Repo
from git.exc import GitCommandError
from git.exc import InvalidGitRepositoryError
from git.exc import NoSuchPathError
from pyrogram import filters

from Cynics import AdminSettings
from Cynics import app
from Cynics import COMMAND_PREFIXES
from Cynics import edit_or_reply
from Cynics import OFFICIAL_BRANCH
from Cynics import REPOSITORY
from Cynics.__main__ import except_hook
from Cynics.__main__ import restart_all
from Cynics.plugins.assistant.updater import update_changelog
from Cynics.utils.capture_errors import capture_err

__MODULE__ = 'Updater'
__HELP__ = """
You want to update latest version?
Easy, just type like bellow

──「 **Check update** 」──
-> `update`
Only check update if avaiable

──「 **Update bot** 」──
-> `update now`
Update your bot to latest version
"""


async def gen_chlog(repo, diff):
    d_form = '%H:%M - %d/%m/%y'
    return ''.join(
        '• [{}]: {} <{}>\n'.format(
            cl.committed_datetime.strftime(d_form),
            cl.summary,
            cl.author,
        )
        for cl in repo.iter_commits(diff)
    )


async def initial_git(repo):
    isexist = os.path.exists('Cynics-old')
    if isexist:
        shutil.rmtree('Cynics-old')
    os.mkdir('Cynics-old')
    os.rename('Cynics', 'Cynics-old/Cynics')
    os.rename('.gitignore', 'Cynics-old/.gitignore')
    os.rename('LICENSE', 'Cynics-old/LICENSE')
    os.rename('README.md', 'Cynics-old/README.md')
    os.rename('requirements.txt', 'Cynics-old/requirements.txt')
    os.rename('Procfile', 'Cynics-old/Procfile')
    os.rename('runtime.txt', 'Cynics-old/runtime.txt')
    update = repo.create_remote('master', REPOSITORY)
    update.pull('master')
    os.rename('Cynics-old/Cynics/config.py', 'Cynics/config.py')
    shutil.rmtree('Cynics/session/')
    os.rename('Cynics-old/Cynics/session/', 'Cynics/session/')


@app.on_message(
    filters.user(AdminSettings) &
    filters.command('update', COMMAND_PREFIXES),
)
@capture_err
async def updater(client, message):
    initial = False
    try:
        repo = Repo()
    except NoSuchPathError as error:
        await edit_or_reply(
            message,
            text='**Update failed!**\n\n'
            f'Error:\n`directory {error} is not found`',
        )
        return
    except InvalidGitRepositoryError:
        repo = Repo.init()
        initial = True
    except GitCommandError as error:
        await edit_or_reply(
            message,
            text=f'**Update failed!**\n\nError:\n`{error}`',
        )
        return

    if initial:
        if len(message.text.split()) != 2:
            await edit_or_reply(
                message,
                text='Your git workdir is missing!\nJust do `update '
                'now` to repair and take update!',
            )
            return
        elif len(
            message.text.split(),
        ) == 2 and message.text.split()[1] == 'now':
            try:
                await initial_git(repo)
            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                await edit_or_reply(message, text=f'**Error:**\n{err}')
                await except_hook(exc_type, exc_obj, exc_tb)
                return
            await edit_or_reply(
                message,
                text='Successfully Updated!\nBot is restarting...',
            )
            await update_changelog(
                '-> **WARNING**: Bot has been created a new git',
            )
            await restart_all()
            return

    brname = repo.active_branch.name
    if brname not in OFFICIAL_BRANCH:
        await edit_or_reply(
            message,
            text='**[UPDATER]:** Looks like you are using your own'
            f'custom branch ({brname}).'
            'in that case, Updater is unable to'
            'identify which branch is to be merged.'
            'please checkout to any official branch',
        )
        return
    try:
        repo.create_remote('upstream', REPOSITORY)
    except BaseException:
        pass

    upstream = repo.remote('upstream')
    upstream.fetch(brname)
    try:
        changelog = await gen_chlog(repo, f'HEAD..upstream/{brname}')
    except Exception as err:
        if 'fatal: bad revision' in str(err):
            try:
                await initial_git(repo)
            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                await edit_or_reply(message, text=f'**Error:**\n{err}')
                await except_hook(exc_type, exc_obj, exc_tb)
                return
            await edit_or_reply(
                message, text='Successfully Updated!\nBot is restarting...',
            )
            await update_changelog(
                '-> **WARNING**: Bot has been created a new git',
            )
            await restart_all()
            return
        exc_type, exc_obj, exc_tb = sys.exc_info()
        await edit_or_reply(
            message,
            text='An error occured!',
        )
        await except_hook(exc_type, exc_obj, exc_tb)
        return

    if not changelog:
        await edit_or_reply(
            message, text=f'Cynics is up-to-date with branch **{brname}**\n',
        )
        return

    if len(message.text.split()) != 2:
        changelog_str = (
            '**To update latest changelog, do**\n - `update now`\n\n'
            f'**New UPDATE available for**: `[{brname}]`\n'
            f'\n**CHANGELOG**:\n`{changelog}` '
        )
        if len(changelog_str) > 4096:
            await edit_or_reply(
                message,
                text='**Changelog is too big, view the file to see it.**',
            )
            with open('Cynics/cache/output.txt', 'w+') as file:
                file.write(changelog_str)
            await client.send_document(
                message.chat.id,
                'Cynics/cache/output.txt',
                reply_to_message_id=message.message_id,
                caption='**Changelog file**',
            )
            os.remove('Cynics/cache/output.txt')
        else:
            await edit_or_reply(message, text=changelog_str)
        return
    elif len(message.text.split()) == 2 and message.text.split()[1] == 'now':
        await edit_or_reply(message, text='`New update found, updating...`')
        try:
            upstream.pull(brname)
            await edit_or_reply(
                message, text='Successfully Updated!\nBot is restarting...',
            )
        except GitCommandError:
            repo.git.reset('--hard')
            repo.git.clean('-fd', 'Cynics/modules/')
            repo.git.clean('-fd', 'Cynics/assistant/')
            repo.git.clean('-fd', 'Cynics/utils/')
            await edit_or_reply(
                message, text='Successfully Updated!\nBot is restarting...',
            )
        await update_changelog(changelog)
        await restart_all()
    else:
        await edit_or_reply(
            message,
            text='**Usage**:\n - `update` to check update\n'
            ' - `update now` to update latest commits\nFor more information ',
        )
