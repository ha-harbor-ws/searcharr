"""
Searcharr
Sonarr & Radarr Telegram Bot
Cancel Callback Utility (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import CallbackQuery

from bot.utils.conversation import delete_conversation
from bot.utils.text import translate
from bot.utils.log import set_up_logger

logger = set_up_logger("callbacks.base.cancel")


async def handle_cancel(callback: CallbackQuery, convo, cid, i, op):
    """Handle cancel and done callbacks."""
    delete_conversation(cid)

    if op == "cancel":
        await callback.message.answer(translate("search_canceled"))

    await callback.message.delete()
    await callback.answer()
