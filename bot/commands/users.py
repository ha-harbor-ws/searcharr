"""
Searcharr
Sonarr & Radarr Telegram Bot
Users Command Handler
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import Message

from bot.utils.auth import authenticated, get_users
from bot.utils.conversation import generate_cid, create_conversation
from bot.utils.formatting import prepare_response_users
from bot.utils.text import translate
from bot.utils.log import set_up_logger
import settings

logger = set_up_logger("commands.users")


async def users_command(message: Message, app):
    """Handle the /users command for user management."""
    username = message.from_user.username if message.from_user else None
    logger.debug(f"Received users cmd from [{username}]")

    auth_level = authenticated(message.from_user.id)
    if not auth_level:
        await message.answer(
            translate(
                "auth_required",
                commands=" OR ".join(
                    [
                        f"`/{c} <{translate('password')}>`"
                        for c in settings.searcharr_start_command_aliases
                    ]
                ),
            )
        )
        return
    elif auth_level != 2:
        await message.answer(
            translate(
                "admin_auth_required",
                commands=" OR ".join(
                    [
                        f"`/{c} <{translate('admin_password')}>`"
                        for c in settings.searcharr_start_command_aliases
                    ]
                ),
            )
        )
        return

    users = get_users()

    cid = generate_cid()
    create_conversation(
        id=cid,
        username=str(username),
        kind="users",
        results=users,
    )

    if not users:
        await message.answer(translate("no_users_found"))
        return

    reply_message, reply_markup = prepare_response_users(
        cid,
        users,
        0,
        5,
        len(users),
    )

    await message.answer(reply_message, reply_markup=reply_markup)
