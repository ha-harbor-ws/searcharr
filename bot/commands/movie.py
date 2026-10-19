"""
Searcharr
Sonarr & Radarr Telegram Bot
Movie Command Handler
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.utils.conversation import generate_cid, create_conversation
from bot.utils.auth import authenticated
from bot.utils.text import strip_entities, translate
from bot.utils.formatting import prepare_response
from bot.utils.log import set_up_logger
import settings

logger = set_up_logger("commands.movie")

FALLBACK_POSTER = (
    "https://artworks.thetvdb.com/banners/images/missing/movie.jpg"
)


async def movie_command(message: Message, app):
    """Handle the /movie command to search for and add movies."""
    username = message.from_user.username if message.from_user else None
    logger.debug(f"Received movie cmd from [{username}]")

    if not authenticated(message.from_user.id):
        await message.answer(
            translate(
                "auth_required",
                commands=" OR ".join(
                    [
                        f"`/{c} <{translate('password')}>`"
                        for c in settings.searcharr_start_command_aliases
                    ]
                ),
            )
        )
        return

    if not settings.radarr_enabled:
        await message.answer(translate("radarr_disabled"))
        return

    title = strip_entities(message)
    if not title:
        x_title = translate("title").title()
        await message.answer(
            translate(
                "include_movie_title_in_cmd",
                commands=" OR ".join(
                    [
                        f"`/{c} {x_title}`"
                        for c in settings.radarr_movie_command_aliases
                    ]
                ),
            )
        )
        return

    results = app.radarr.lookup_movie(title)

    if not results:
        await message.answer(translate("no_matching_movies"))
        return

    cid = generate_cid()
    if not cid:
        await message.answer(translate("unexpected_error"))
        return

    create_conversation(
        id=cid,
        username=str(username),
        kind="movie",
        results=results,
    )

    r = results[0]
    reply_message, reply_markup = prepare_response(
        "movie", r, cid, 0, len(results)
    )

    try:
        await message.answer_photo(
            photo=r["remotePoster"],
            caption=reply_message,
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
                f"Error sending photo [{r['remotePoster']}]: {e}. "
                "Attempting to send with default poster..."
            )
            await message.answer_photo(
                photo=FALLBACK_POSTER,
                caption=reply_message,
                reply_markup=reply_markup,
            )
        else:
            raise
