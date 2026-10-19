#!/usr/bin/env python3
"""
Searcharr
Sonarr & Radarr Telegram Bot (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
# Settings must be loaded first (registers in sys.modules)
from config.settings_loader import load_settings

load_settings()

# Now safe to import modules that use `import settings`
import argparse

import settings
from bot.searcharr_bot import SearcharrBot
from bot.utils.log import set_up_logger, configure_logging
from config.settings_loader import check_settings_migration

__version__ = "4.0.0"


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Searcharr", description="Start the Searcharr Bot."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        dest="verbose",
        help="Enable debug logging.",
    )
    parser.add_argument(
        "--console-logging",
        "-c",
        action="store_true",
        dest="console_logging",
        help="Enable console logging.",
    )
    parser.add_argument(
        "--dev",
        "-d",
        action="store_true",
        dest="dev_mode",
        help="Enable developer mode, which will result in more exceptions being raised instead of handled.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    configure_logging(args.verbose, args.console_logging)
    logger = set_up_logger("searcharr")
    check_settings_migration()

    logger.info(f"Searcharr v{__version__} (Aiogram) - Starting...")

    bot = SearcharrBot(
        token=settings.tgram_token,
        api_url=getattr(settings, "tg_local_api_url", None),
        dev_mode=args.dev_mode,
        verbose=args.verbose,
    )

    bot.run()
