"""
Searcharr
Sonarr & Radarr Telegram Bot
Photo Media Utilities (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto

from bot.utils.log import set_up_logger

logger = set_up_logger("callbacks.base.media_message")

FALLBACK_POSTER = (
    "https://artworks.thetvdb.com/banners/images/missing/movie.jpg"
)


async def update_media_message(
    message,
    media_url,
    caption=None,
    reply_markup=None,
    fallback_url=FALLBACK_POSTER,
):
    """Edit a message photo, falling back to a default image on BadRequest."""
    try:
        return await message.edit_media(
            media=InputMediaPhoto(media=media_url, caption=caption),
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as e:
        err = str(e)
        if any(
            x in err
            for x in (
                "Wrong type of the web page content",
                "Wrong file identifier/http url specified",
                "Media_empty",
            )
        ):
            logger.error(
                f"Error sending photo [{media_url}]: TelegramBadRequest: {e}. "
                "Attempting to send with default poster..."
            )
            return await message.edit_media(
                media=InputMediaPhoto(media=fallback_url, caption=caption),
                reply_markup=reply_markup,
            )
        raise
