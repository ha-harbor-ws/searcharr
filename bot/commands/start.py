"""
Searcharr
Sonarr & Radarr Telegram Bot
Start Command Handler
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import Message

from bot.utils.auth import add_user, authenticated
from bot.utils.text import strip_entities, translate
from bot.utils.log import set_up_logger
import settings

logger = set_up_logger("commands.start")


async def start_command(message: Message, app):
    """Handle the /start command for authentication."""
    username = message.from_user.username if message.from_user else None
    logger.debug(f"Received start cmd from [{username}]")

    password = strip_entities(message)

    if password and password == settings.searcharr_admin_password:
        add_user(
            id=message.from_user.id,
            username=str(username),
            admin=1,
        )
        await message.answer(
            translate(
                "admin_auth_success",
                commands=" OR ".join(
                    [f"`/{c}`" for c in settings.searcharr_help_command_aliases]
                ),
            )
        )
    elif authenticated(message.from_user.id):
        await message.answer(
            translate(
                "already_authenticated",
                commands=" OR ".join(
                    [f"`/{c}`" for c in settings.searcharr_help_command_aliases]
                ),
            )
        )
    elif password == settings.searcharr_password:
        add_user(
            id=message.from_user.id,
            username=str(username),
        )
        await message.answer(
            translate(
                "auth_successful",
                commands=" OR ".join(
                    [f"`/{c}`" for c in settings.searcharr_help_command_aliases]
                ),
            )
        )
    else:
        await message.answer(translate("incorrect_pw"))
