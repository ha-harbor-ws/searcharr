"""
Searcharr
Aiogram middleware: inject SearcharrBot into handler data.
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AppMiddleware(BaseMiddleware):
    """Puts the SearcharrBot instance into handler kwargs as ``app``."""

    def __init__(self, app):
        self.app = app

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["app"] = self.app
        return await handler(event, data)
