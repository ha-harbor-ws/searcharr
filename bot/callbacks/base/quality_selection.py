"""
Searcharr
Sonarr & Radarr Telegram Bot
Quality Profile Selection Utility (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import CallbackQuery

from bot.callbacks.base.media_message import update_media_message
from bot.utils.conversation import get_add_data, update_add_data, delete_conversation
from bot.utils.formatting import prepare_response
from bot.utils.text import translate
from bot.utils.log import set_up_logger

logger = set_up_logger("callbacks.base.quality_selection")


async def check_quality_selection(
    callback: CallbackQuery, service, kind, convo, cid, i
):
    """Check and handle quality profile selection.

    Returns True to continue, False if waiting for user input / cancelled.
    """
    r = convo["results"][i]
    additional_data = get_add_data(cid)

    if not additional_data.get("q"):
        quality_profiles = service._quality_profiles
        if len(quality_profiles) > 1:
            reply_message, reply_markup = prepare_response(
                kind,
                r,
                cid,
                i,
                len(convo["results"]),
                add=True,
                quality_profiles=quality_profiles,
            )
            await update_media_message(
                callback.message,
                r["remotePoster"],
                caption=reply_message,
                reply_markup=reply_markup,
            )
            await callback.answer()
            return False

        if len(quality_profiles) == 1:
            logger.debug(
                f"Only one quality profile enabled. Adding/Updating additional data "
                f"for cid=[{cid}], key=[q], value=[{quality_profiles[0]['id']}]..."
            )
            update_add_data(cid, "q", quality_profiles[0]["id"])
        else:
            delete_conversation(cid)
            service_name = "Sonarr" if kind == "series" else "Radarr"
            await callback.message.answer(
                translate(
                    "no_quality_profiles",
                    kind=translate(kind),
                    app=service_name,
                )
            )
            await callback.message.delete()
            await callback.answer()
            return False

    return True
