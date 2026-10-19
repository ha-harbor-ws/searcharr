"""
Searcharr
Sonarr & Radarr Telegram Bot
Path Selection Utility (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import CallbackQuery

from bot.callbacks.base.media_message import update_media_message
from bot.utils.conversation import get_add_data, update_add_data, delete_conversation
from bot.utils.formatting import prepare_response
from bot.utils.text import translate
from bot.utils.log import set_up_logger

logger = set_up_logger("callbacks.base.path_selection")


async def check_path_selection(callback: CallbackQuery, service, kind, convo, cid, i):
    """Check and handle root folder selection.

    Returns True to continue, False if waiting for user input / cancelled.
    """
    r = convo["results"][i]
    additional_data = get_add_data(cid)

    if not additional_data.get("p"):
        paths = service._root_folders
        if len(paths) > 1:
            reply_message, reply_markup = prepare_response(
                kind,
                r,
                cid,
                i,
                len(convo["results"]),
                add=True,
                paths=paths,
            )
            await update_media_message(
                callback.message,
                r["remotePoster"],
                caption=reply_message,
                reply_markup=reply_markup,
            )
            await callback.answer()
            return False

        if len(paths) == 1:
            logger.debug(
                f"Only one root folder enabled. Adding/Updating additional data "
                f"for cid=[{cid}], key=[p], value=[{paths[0]['path']}]..."
            )
            update_add_data(cid, "p", paths[0]["path"])
        else:
            delete_conversation(cid)
            service_name = "Sonarr" if kind == "series" else "Radarr"
            await callback.message.answer(
                translate(
                    "no_root_folders",
                    kind=translate(kind),
                    app=service_name,
                )
            )
            await callback.message.delete()
            await callback.answer()
            return False
    else:
        try:
            int(additional_data.get("p"))
        except ValueError:
            pass
        else:
            paths = service._root_folders
            path = next(
                (p["path"] for p in paths if p["id"] == int(additional_data["p"])),
                None,
            )
            logger.debug(
                f"Path id [{additional_data['p']}] lookup result: [{path}]"
            )
            if path:
                update_add_data(cid, "p", path)

    return True
