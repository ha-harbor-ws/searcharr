"""
Searcharr
Sonarr & Radarr Telegram Bot
Callback Handler Package Initialization
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from bot.callbacks.callback_handler import create_callbacks_router, main_callback_handler

__all__ = ["create_callbacks_router", "main_callback_handler"]
