"""
Searcharr
Sonarr & Radarr Telegram Bot
User Management Callback Handlers (Aiogram)
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import CallbackQuery

from bot.utils.auth import remove_user, update_admin_access, get_users, authenticated
from bot.utils.conversation import create_conversation
from bot.utils.formatting import prepare_response_users
from bot.utils.text import translate
from bot.utils.log import set_up_logger
from bot.callbacks.base import handle_cancel
import settings

logger = set_up_logger("callbacks.user_management")


async def handle_user_callback(callback: CallbackQuery, app, convo, cid, i, op, op_flags):
    """Handle callbacks related to user management."""
    if op in ("cancel", "done"):
        await handle_cancel(callback, convo, cid, i, op)
        return

    user_id = i

    auth_level = await check_admin_auth(callback)
    if auth_level != 2:
        return

    try:
        if op == "remove_user":
            await handle_remove_user(callback, convo, cid, user_id)
        elif op == "make_admin":
            await handle_make_admin(callback, convo, cid, user_id)
        elif op == "remove_admin":
            await handle_remove_admin(callback, convo, cid, user_id)
        elif op in ("prev", "next"):
            await handle_user_navigation(callback, convo, cid, i, op)
        else:
            await callback.answer()
    except Exception as e:
        logger.error(f"Error in user management callback: {e}")
        await callback.message.answer(translate("unexpected_error"))
        await callback.answer()


async def check_admin_auth(callback: CallbackQuery):
    """Check if the user has admin privileges."""
    auth_level = authenticated(callback.from_user.id)

    if auth_level != 2:
        await callback.message.answer(
            translate(
                "admin_auth_required",
                commands=" OR ".join(
                    [
                        f"`/{c} <{translate('admin_password')}>`"
                        for c in settings.searcharr_start_command_aliases
                    ]
                ),
            )
        )
        await callback.message.delete()
        await callback.answer()

    return auth_level


async def handle_remove_user(callback: CallbackQuery, convo, cid, user_id):
    """Handle the remove_user operation."""
    try:
        remove_user(user_id)

        updated_users = get_users()
        create_conversation(
            id=cid,
            username=str(callback.from_user.username),
            kind="users",
            results=updated_users,
        )

        reply_message, reply_markup = prepare_response_users(
            cid,
            updated_users,
            0,
            5,
            len(updated_users),
        )

        await callback.message.edit_text(
            text=f"{translate('removed_user', user=user_id)} {reply_message}",
            reply_markup=reply_markup,
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error removing all access for user id [{user_id}]: {e}")
        await callback.message.answer(
            translate("unknown_error_removing_user", user=user_id)
        )
        await callback.answer()


async def handle_make_admin(callback: CallbackQuery, convo, cid, user_id):
    """Handle the make_admin operation."""
    try:
        update_admin_access(user_id, 1)

        updated_users = get_users()
        create_conversation(
            id=cid,
            username=str(callback.from_user.username),
            kind="users",
            results=updated_users,
        )

        reply_message, reply_markup = prepare_response_users(
            cid,
            updated_users,
            0,
            5,
            len(updated_users),
        )

        await callback.message.edit_text(
            text=f"{translate('added_admin_access', user=user_id)} {reply_message}",
            reply_markup=reply_markup,
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error adding admin access for user id [{user_id}]: {e}")
        await callback.message.answer(
            translate("unknown_error_adding_admin", user=user_id)
        )
        await callback.answer()


async def handle_remove_admin(callback: CallbackQuery, convo, cid, user_id):
    """Handle the remove_admin operation."""
    try:
        update_admin_access(user_id, "")

        updated_users = get_users()
        create_conversation(
            id=cid,
            username=str(callback.from_user.username),
            kind="users",
            results=updated_users,
        )

        reply_message, reply_markup = prepare_response_users(
            cid,
            updated_users,
            0,
            5,
            len(updated_users),
        )

        await callback.message.edit_text(
            text=f"{translate('removed_admin_access', user=user_id)} {reply_message}",
            reply_markup=reply_markup,
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error removing admin access for user id [{user_id}]: {e}")
        await callback.message.answer(
            translate("unknown_error_removing_admin", user=user_id)
        )
        await callback.answer()


async def handle_user_navigation(callback: CallbackQuery, convo, cid, offset, op):
    """Handle navigation for user management (prev/next pages)."""
    page_size = 5

    if op == "prev":
        new_offset = max(0, offset - page_size)
    elif op == "next":
        new_offset = min(len(convo["results"]) - 1, offset + page_size)
    else:
        new_offset = offset

    reply_message, reply_markup = prepare_response_users(
        cid,
        convo["results"],
        new_offset,
        page_size,
        len(convo["results"]),
    )

    await callback.message.edit_text(
        text=reply_message,
        reply_markup=reply_markup,
    )
    await callback.answer()
