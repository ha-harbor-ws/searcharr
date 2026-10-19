"""
Searcharr
Sonarr & Radarr Telegram Bot
Message Formatting Utilities
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.text import translate
from bot.utils.log import set_up_logger

logger = set_up_logger("formatting")


def prepare_response(
    kind,
    r,
    cid,
    i,
    total_results,
    add=False,
    paths=None,
    quality_profiles=None,
    monitor_options=None,
    tags=None,
):
    """Prepare a response message and keyboard markup."""
    keyboard = []
    keyboard_nav_row = []

    if i > 0:
        keyboard_nav_row.append(
            InlineKeyboardButton(
                text=translate("prev_button"),
                callback_data=f"{cid}^^^{i}^^^prev",
            )
        )

    if kind == "series" and r["tvdbId"]:
        keyboard_nav_row.append(
            InlineKeyboardButton(
                text="tvdb",
                url=f"https://thetvdb.com/series/{r['titleSlug']}",
            )
        )
    elif kind == "movie" and r["tmdbId"]:
        keyboard_nav_row.append(
            InlineKeyboardButton(
                text="TMDB",
                url=f"https://www.themoviedb.org/movie/{r['tmdbId']}",
            )
        )

    if kind in ["series", "movie"] and r["imdbId"]:
        keyboard_nav_row.append(
            InlineKeyboardButton(
                text="IMDb",
                url=f"https://imdb.com/title/{r['imdbId']}",
            )
        )

    if total_results > 1 and i < total_results - 1:
        keyboard_nav_row.append(
            InlineKeyboardButton(
                text=translate("next_button"),
                callback_data=f"{cid}^^^{i}^^^next",
            )
        )

    keyboard.append(keyboard_nav_row)

    if add:
        if tags:
            for tag in tags[:12]:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=translate("add_tag_button", tag=tag["label"]),
                            callback_data=f"{cid}^^^{i}^^^add^^^tt={tag['id']}",
                        )
                    ]
                )
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=translate("finished_tagging_button"),
                        callback_data=f"{cid}^^^{i}^^^add^^^td=1",
                    )
                ]
            )
        elif monitor_options:
            for k, o in enumerate(monitor_options):
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=translate("monitor_button", option=o),
                            callback_data=f"{cid}^^^{i}^^^add^^^m={k}",
                        )
                    ]
                )
        elif quality_profiles:
            for q in quality_profiles:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=translate("add_quality_button", quality=q["name"]),
                            callback_data=f"{cid}^^^{i}^^^add^^^q={q['id']}",
                        )
                    ]
                )
        elif paths:
            for p in paths:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=translate("add_path_button", path=p["path"]),
                            callback_data=f"{cid}^^^{i}^^^add^^^p={p['id']}",
                        )
                    ]
                )

    keyboard_act_row = []
    if not add:
        if not r["id"]:
            keyboard_act_row.append(
                InlineKeyboardButton(
                    text=translate("add_button", kind=translate(kind).title()),
                    callback_data=f"{cid}^^^{i}^^^add",
                )
            )
        else:
            keyboard_act_row.append(
                InlineKeyboardButton(
                    text=translate("already_added_button"),
                    callback_data=f"{cid}^^^{i}^^^noop",
                )
            )

    keyboard_act_row.append(
        InlineKeyboardButton(
            text=translate("cancel_search_button"),
            callback_data=f"{cid}^^^{i}^^^cancel",
        )
    )

    if keyboard_act_row:
        keyboard.append(keyboard_act_row)

    if not add and kind == "series" and "Anime" in r.get("genres", []):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=translate("add_series_anime_button"),
                    callback_data=f"{cid}^^^{i}^^^add^^^st=a",
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if kind == "series":
        reply_message = (
            f"{r['title']}"
            f"{' (' + str(r['year']) + ')' if r['year'] and str(r['year']) not in r['title'] else ''}"
            f" - {r['seasonCount']} Season{'s' if r['seasonCount'] != 1 else ''}"
            f"{' - ' + r['network'] if r['network'] else ''}"
            f" - {r['status'].title()}\n\n{r['overview']}"
        )[0:1024]
    elif kind == "movie":
        reply_message = (
            f"{r['title']}"
            f"{' (' + str(r['year']) + ')' if r['year'] and str(r['year']) not in r['title'] else ''}"
            f"{' - ' + str(r['runtime']) + ' min' if r['runtime'] else ''}"
            f" - {r['status'].title()}\n\n{r['overview']}"
        )[0:1024]
    else:
        reply_message = translate("unexpected_error")

    return (reply_message, reply_markup)


def prepare_response_users(cid, users, offset, num, total_results):
    """Prepare a response message and keyboard markup for user management."""
    keyboard = []

    for u in users[offset : offset + num]:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=translate("remove_user_button"),
                    callback_data=f"{cid}^^^{u['id']}^^^remove_user",
                ),
                InlineKeyboardButton(
                    text=f"{u['username'] if u['username'] != 'None' else u['id']}",
                    callback_data=f"{cid}^^^{u['id']}^^^noop",
                ),
                InlineKeyboardButton(
                    text=translate("remove_admin_button")
                    if u["admin"]
                    else translate("make_admin_button"),
                    callback_data=(
                        f"{cid}^^^{u['id']}^^^{'remove_admin' if u['admin'] else 'make_admin'}"
                    ),
                ),
            ]
        )

    keyboard_nav_row = []
    if offset > 0:
        keyboard_nav_row.append(
            InlineKeyboardButton(
                text=translate("prev_button"),
                callback_data=f"{cid}^^^{offset - num}^^^prev",
            )
        )

    keyboard_nav_row.append(
        InlineKeyboardButton(
            text=translate("done"),
            callback_data=f"{cid}^^^{offset}^^^done",
        )
    )

    if total_results > 1 and offset + num < total_results:
        keyboard_nav_row.append(
            InlineKeyboardButton(
                text=translate("next_button"),
                callback_data=f"{cid}^^^{offset + num}^^^next",
            )
        )

    keyboard.append(keyboard_nav_row)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    reply_message = translate(
        "listing_users_pagination",
        page_info=f"{offset + 1}-{min(offset + num, total_results)} of {total_results}",
    )

    return (reply_message, reply_markup)
