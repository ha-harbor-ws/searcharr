"""
Searcharr
Sonarr & Radarr Telegram Bot
Command Handlers Registration (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram import Router
from aiogram.filters import Command

import settings
from bot.commands.start import start_command
from bot.commands.help import help_command
from bot.commands.series import series_command
from bot.commands.movie import movie_command
from bot.commands.users import users_command


def create_commands_router(app) -> Router:
    """Create and configure the commands router."""
    router = Router(name="commands")
    logger = app.logger

    aliases = settings.searcharr_help_command_aliases
    logger.debug(f"Registering help commands: {aliases}")
    router.message.register(help_command, Command(*aliases))

    aliases = settings.searcharr_start_command_aliases
    logger.debug(f"Registering start commands: {aliases}")
    router.message.register(start_command, Command(*aliases))

    if app.sonarr:
        aliases = settings.sonarr_series_command_aliases
        logger.debug(f"Registering series commands: {aliases}")
        router.message.register(series_command, Command(*aliases))

    if app.radarr:
        aliases = settings.radarr_movie_command_aliases
        logger.debug(f"Registering movie commands: {aliases}")
        router.message.register(movie_command, Command(*aliases))

    aliases = settings.searcharr_users_command_aliases
    logger.debug(f"Registering users commands: {aliases}")
    router.message.register(users_command, Command(*aliases))

    return router
