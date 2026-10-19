"""
Searcharr
Sonarr & Radarr Telegram Bot
Navigation Utilities (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import CallbackQuery

from bot.callbacks.base.media_message import update_media_message
from bot.utils.formatting import prepare_response
from bot.utils.log import set_up_logger

logger = set_up_logger("callbacks.base.navigation")


async def handle_navigation(callback: CallbackQuery, kind, convo, cid, i, op):
    """Handle navigation callbacks (prev/next) for content browsing."""
    if op == "prev":
        if i <= 0:
            await callback.answer()
            return True

        r = convo["results"][i - 1]
        reply_message, reply_markup = prepare_response(
            kind, r, cid, i - 1, len(convo["results"])
        )
        await update_media_message(
            callback.message,
            r["remotePoster"],
            caption=reply_message,
            reply_markup=reply_markup,
        )

    elif op == "next":
        if i >= len(convo["results"]) - 1:
            await callback.answer()
            return True

        r = convo["results"][i + 1]
        reply_message, reply_markup = prepare_response(
            kind, r, cid, i + 1, len(convo["results"])
        )
        await update_media_message(
            callback.message,
            r["remotePoster"],
            caption=reply_message,
            reply_markup=reply_markup,
        )

    await callback.answer()
    return True
