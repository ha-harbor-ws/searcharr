"""
Searcharr
Sonarr & Radarr Telegram Bot
Main Bot Class (Aiogram 3)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import ErrorEvent

from api.sonarr import Sonarr
from api.radarr import Radarr
from bot.utils.log import set_up_logger
from bot.utils.database import init_db
from bot.commands import create_commands_router
from bot.callbacks import create_callbacks_router
from bot.middlewares import AppMiddleware
import settings
from config.language import load_language


class SearcharrBot:
    """Main Searcharr bot class that initializes and runs the Telegram bot."""

    def __init__(self, token, api_url=None, dev_mode=False, verbose=False):
        """Initialize the Searcharr bot.

        Args:
            token (str): Telegram bot token
            api_url (str, optional): Local Telegram Bot API base URL
                (e.g. http://127.0.0.1:8081). Empty/None uses api.telegram.org.
            dev_mode (bool, optional): Enable developer mode. Defaults to False.
            verbose (bool, optional): Enable verbose logging. Defaults to False.
        """
        self.dev_mode = dev_mode
        self.token = token
        self.api_url = (api_url or "").strip() or None
        self.local_mode = bool(getattr(settings, "tg_local_mode", False))
        self.logger = set_up_logger("bot")
        self.logger.info("Initializing SearcharrBot (Aiogram)...")

        init_db()
        self.lang = load_language()

        self.sonarr = self._init_service("sonarr", verbose)
        self.radarr = self._init_service("radarr", verbose)

        self._validate_settings()
        self.ai = self._init_ai()
        if self.ai and self.ai.enabled:
            from bot.utils.ai_prefs import ensure_ai_prefs_schema

            ensure_ai_prefs_schema()

    def _init_service(self, service_name, verbose):
        """Initialize a service client with error handling."""
        enabled_setting = f"{service_name}_enabled"
        if not hasattr(settings, enabled_setting):
            setattr(settings, enabled_setting, False)
            self.logger.warning(
                f"No {enabled_setting} setting found. If you want Searcharr to support "
                f"{service_name.title()}, please refer to the sample settings on github "
                f"and add settings for {service_name.title()} to settings.py."
            )
            return None
        elif not getattr(settings, enabled_setting):
            self.logger.info(f"{service_name.title()} is disabled in settings")
            return None

        try:
            if service_name == "sonarr":
                from bot.services.sonarr_service import configure_sonarr

                client = Sonarr(settings.sonarr_url, settings.sonarr_api_key, verbose)
                return configure_sonarr(client)

            if service_name == "radarr":
                from bot.services.radarr_service import configure_radarr

                client = Radarr(settings.radarr_url, settings.radarr_api_key, verbose)
                return configure_radarr(client)

            self.logger.error(f"Unknown service: {service_name}")
            return None

        except Exception as e:
            self.logger.error(f"Failed to initialize {service_name.title()}: {e}")
            setattr(settings, f"{service_name}_enabled", False)
            return None

    def _init_ai(self):
        """Initialize optional AI chat service."""
        try:
            from bot.services.ai_service import AiChatService

            return AiChatService()
        except Exception as e:
            self.logger.error(f"Failed to initialize AI chat: {e}")
            return None

    def _validate_settings(self):
        """Validate and set defaults for settings."""
        from config.validator import validate_settings

        validate_settings()

    def _create_bot(self) -> Bot:
        """Create an Aiogram Bot, optionally pointed at a local Bot API server."""
        session = None
        if self.api_url:
            base = self.api_url.rstrip("/")
            if base.endswith("/bot"):
                base = base[: -len("/bot")]
            self.logger.info(
                f"Using local Telegram Bot API: base={base}, local_mode={self.local_mode}"
            )
            session = AiohttpSession(
                api=TelegramAPIServer.from_base(base, is_local=self.local_mode)
            )

        return Bot(
            token=self.token,
            session=session,
            default=DefaultBotProperties(),
        )

    async def _run_async(self):
        """Build dispatcher and start polling."""
        self.logger.info("Starting Searcharr bot (Aiogram polling)...")

        bot = self._create_bot()
        dp = Dispatcher()

        dp.update.middleware(AppMiddleware(self))
        dp.include_router(create_commands_router(self))
        dp.include_router(create_callbacks_router(self))

        if not self.dev_mode:

            @dp.errors()
            async def on_error(event: ErrorEvent):
                self.logger.error(f"Error occurred: {event.exception}")

        else:
            self.logger.info(
                "Developer mode is enabled; exceptions will propagate."
            )

        if self.ai and self.ai.enabled:
            await self.ai.start_persistence()

        try:
            await dp.start_polling(bot)
        finally:
            if self.ai and self.ai.enabled:
                await self.ai.stop_persistence()
            await bot.session.close()

    def run(self):
        """Initialize and run the Telegram bot."""
        asyncio.run(self._run_async())
