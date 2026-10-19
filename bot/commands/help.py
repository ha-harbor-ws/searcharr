"""
Searcharr
Sonarr & Radarr Telegram Bot
Help Command Handler
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import Message

from bot.utils.auth import authenticated
from bot.utils.text import translate
from bot.utils.log import set_up_logger
import settings

logger = set_up_logger("commands.help")


async def help_command(message: Message, app):
    """Handle the /help command to provide usage information."""
    username = message.from_user.username if message.from_user else None
    logger.debug(f"Received help cmd from [{username}]")

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

    help_text = []

    if settings.sonarr_enabled:
        help_text.append(
            translate(
                "help_sonarr",
                series_commands=" OR ".join(
                    [
                        f"`/{c} {translate('title').title()}`"
                        for c in settings.sonarr_series_command_aliases
                    ]
                ),
            )
        )

    if settings.radarr_enabled:
        help_text.append(
            translate(
                "help_radarr",
                movie_commands=" OR ".join(
                    [
                        f"`/{c} {translate('title').title()}`"
                        for c in settings.radarr_movie_command_aliases
                    ]
                ),
            )
        )

    if getattr(app, "ai", None) and app.ai.enabled:
        help_text.append(
            translate(
                "help_ai",
                ai_commands=" OR ".join(
                    [
                        f"`/{c}`"
                        for c in getattr(settings, "ai_command_aliases", ["ai"])
                    ]
                ),
            )
        )

    if auth_level == 2:
        help_text.append(
            translate(
                "admin_help",
                commands=" OR ".join(
                    [f"`/{c}`" for c in settings.searcharr_users_command_aliases]
                ),
            )
        )

    if help_text:
        await message.answer(" ".join(help_text))
    else:
        await message.answer(translate("no_features"))
