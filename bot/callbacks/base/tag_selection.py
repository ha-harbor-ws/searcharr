"""
Searcharr
Sonarr & Radarr Telegram Bot
Tag Selection Utilities (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import CallbackQuery

from bot.callbacks.base.media_message import update_media_message
from bot.utils.conversation import get_add_data, update_add_data
from bot.utils.formatting import prepare_response
from bot.utils.log import set_up_logger

logger = set_up_logger("callbacks.base.tag_selection")


async def handle_tag_selection(
    callback: CallbackQuery, service, service_config, convo, cid, i, op_flags
):
    """Handle tag selection for content.

    Returns True if tag selection UI was shown, False to proceed.
    """
    r = convo["results"][i]

    if not op_flags.get("tt") and not op_flags.get("td"):
        return False

    additional_data = get_add_data(cid)

    if op_flags.get("tt"):
        tag_id = op_flags.get("tt")
        tag_ids = (
            additional_data.get("t", "").split(",")
            if len(additional_data.get("t", ""))
            else []
        )

        if tag_id not in tag_ids:
            tag_ids.append(tag_id)
            logger.debug(f"Adding tag [{tag_id}]")
            update_add_data(cid, "t", ",".join(tag_ids))

        all_tags = service.get_filtered_tags(
            service_config.get("user_selectable_tags", []),
            service_config.get("forced_tags", []),
        )
        selected_ids = set(get_add_data(cid).get("t", "").split(","))
        remaining_tags = [t for t in all_tags if str(t["id"]) not in selected_ids]

        if not remaining_tags:
            await callback.answer()
            return False

        reply_message, reply_markup = prepare_response(
            convo["type"],
            r,
            cid,
            i,
            len(convo["results"]),
            add=True,
            tags=remaining_tags,
        )
        await update_media_message(
            callback.message,
            r["remotePoster"],
            caption=reply_message,
            reply_markup=reply_markup,
        )
        await callback.answer()
        return True

    if op_flags.get("td"):
        update_add_data(cid, "td", "1")
        await callback.answer()
        return False

    return False


async def process_tags(service, service_config, cid, user):
    """Process tags for content (username tag and forced tags)."""
    additional_data = get_add_data(cid)

    tags = (
        additional_data.get("t").split(",")
        if len(additional_data.get("t", ""))
        else []
    )
    logger.debug(f"Current tags: {tags}")

    if service_config.get("tag_with_username", True):
        tag = f"searcharr-{user.username if user.username else user.id}"
        if tag_id := service.get_tag_id(tag):
            tags.append(str(tag_id))
        else:
            logger.warning(
                f"Tag lookup/creation failed for [{tag}]. "
                "This tag will not be added to the content."
            )

    for tag in service_config.get("forced_tags", []):
        if tag_id := service.get_tag_id(tag):
            tags.append(str(tag_id))
        else:
            logger.warning(
                f"Tag lookup/creation failed for forced tag [{tag}]. "
                "This tag will not be added to the content."
            )

    update_add_data(cid, "t", ",".join(list(set(tags))))
    return True
