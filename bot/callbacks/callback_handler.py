"""
Searcharr
Sonarr & Radarr Telegram Bot
Main Callback Router (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram import Router
from aiogram.types import CallbackQuery

from bot.utils.conversation import get_conversation
from bot.utils.log import set_up_logger
from bot.callbacks.sonarr_callbacks import handle_sonarr_callback
from bot.callbacks.radarr_callbacks import handle_radarr_callback
from bot.callbacks.user_callbacks import handle_user_callback

logger = set_up_logger("callbacks.handler")


def create_callbacks_router(app) -> Router:
    """Create the inline callback router."""
    router = Router(name="callbacks")

    @router.callback_query()
    async def handle_callback(callback: CallbackQuery, app):
        data = (callback.data or "").split("^^^")

        if len(data) < 3:
            logger.error(f"Invalid callback data: {callback.data}")
            await callback.answer()
            return

        cid, i, op = data[0], int(data[1]), data[2]

        op_flags = {}
        if len(data) > 3 and data[3]:
            for flag in data[3].split("^"):
                if "=" in flag:
                    k, v = flag.split("=", 1)
                    op_flags[k] = v

        convo = get_conversation(cid)
        if not convo:
            logger.warning(f"No conversation found with id: {cid}")
            await callback.answer()
            return

        try:
            if convo["type"] == "series":
                await handle_sonarr_callback(
                    callback, app, convo, cid, i, op, op_flags
                )
            elif convo["type"] == "movie":
                await handle_radarr_callback(
                    callback, app, convo, cid, i, op, op_flags
                )
            elif convo["type"] == "users":
                await handle_user_callback(
                    callback, app, convo, cid, i, op, op_flags
                )
            else:
                logger.error(f"Unknown conversation type: {convo['type']}")
                await callback.answer()
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            if app.dev_mode:
                raise
            await callback.answer()

    return router


def main_callback_handler(bot):
    """Compatibility alias — prefer create_callbacks_router."""
    return create_callbacks_router(bot)
