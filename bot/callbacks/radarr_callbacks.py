"""
Searcharr
Sonarr & Radarr Telegram Bot
Radarr-Specific Callback Handlers (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import CallbackQuery

from bot.utils.conversation import get_add_data, update_add_data, delete_conversation
from bot.utils.formatting import prepare_response
from bot.utils.text import translate
from bot.utils.log import set_up_logger
from bot.callbacks.base import (
    handle_navigation,
    handle_cancel,
    check_path_selection,
    check_quality_selection,
    handle_tag_selection,
    process_tags,
    update_media_message,
)
import settings

logger = set_up_logger("callbacks.radarr")


def _radarr_config():
    return {
        "tag_with_username": settings.radarr_tag_with_username,
        "forced_tags": settings.radarr_forced_tags,
        "allow_user_to_select_tags": settings.radarr_allow_user_to_select_tags,
        "user_selectable_tags": settings.radarr_user_selectable_tags,
        "add_monitored": settings.radarr_add_monitored,
        "search_on_add": settings.radarr_search_on_add,
        "min_availability": settings.radarr_min_availability,
    }


async def handle_radarr_callback(callback: CallbackQuery, app, convo, cid, i, op, op_flags):
    """Handle callbacks related to Radarr (movies)."""
    if op == "add":
        await handle_add_movie(callback, app, convo, cid, i, op_flags)
    elif op in ("prev", "next"):
        await handle_navigation(callback, "movie", convo, cid, i, op)
    elif op in ("cancel", "done"):
        await handle_cancel(callback, convo, cid, i, op)
    else:
        await callback.answer()


async def handle_add_movie(callback: CallbackQuery, app, convo, cid, i, op_flags):
    """Handle adding a movie to Radarr."""
    service = app.radarr
    config = _radarr_config()
    r = convo["results"][i]

    if op_flags:
        for k, v in op_flags.items():
            logger.debug(
                f"Adding/Updating additional data for cid=[{cid}], key=[{k}], value=[{v}]..."
            )
            update_add_data(cid, k, v)

        if op_flags.get("tt") or op_flags.get("td"):
            handled = await handle_tag_selection(
                callback, service, config, convo, cid, i, op_flags
            )
            if handled:
                return

    additional_data = get_add_data(cid)
    logger.debug(f"Additional data: {additional_data}")

    if not await check_path_selection(callback, service, "movie", convo, cid, i):
        return

    if not await check_quality_selection(callback, service, "movie", convo, cid, i):
        return

    if config["allow_user_to_select_tags"] and not additional_data.get("td"):
        all_tags = service.get_filtered_tags(
            config["user_selectable_tags"],
            config["forced_tags"],
        )

        if all_tags and not additional_data.get("tt"):
            reply_message, reply_markup = prepare_response(
                "movie",
                r,
                cid,
                i,
                len(convo["results"]),
                add=True,
                tags=all_tags,
            )
            await update_media_message(
                callback.message,
                r["remotePoster"],
                caption=reply_message,
                reply_markup=reply_markup,
            )
            await callback.answer()
            return

    await process_tags(service, config, cid, callback.from_user)

    logger.debug("All data is accounted for, proceeding to add...")
    try:
        added = service.add_movie(
            movie_info=r,
            monitored=config["add_monitored"],
            search=config["search_on_add"],
            min_avail=config["min_availability"],
            additional_data=get_add_data(cid),
        )
    except Exception as e:
        logger.error(f"Error adding movie: {e}")
        added = False

    logger.debug(f"Result of attempt to add movie: {added}")

    if added:
        delete_conversation(cid)
        await callback.message.answer(translate("added", title=r["title"]))
        await callback.message.delete()
    else:
        await callback.message.answer(
            translate("unknown_error_adding", kind="movie")
        )

    await callback.answer()
