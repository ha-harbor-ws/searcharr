"""
Searcharr AI chat: private + group modes with admin voice commands.
"""
from aiogram import F
from aiogram.enums import ChatAction, ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.utils.auth import authenticated
from bot.utils.ai_prefs import (
    MODE_LISTEN_ALL,
    MODE_MENTION_ONLY,
    get_group_mode,
    is_private_enabled,
    set_group_mode,
    set_private_enabled,
)
from bot.utils.text import translate
from bot.utils.log import set_up_logger
import settings

logger = set_up_logger("commands.ai_chat")

# Admin voice commands (substring match, case-insensitive)
ADMIN_CMD_MENTION_ONLY = "не влезай в разговор"
ADMIN_CMD_LISTEN_ALL = "поговори с нами"
ADMIN_CMD_PRIVATE_OFF = "хватит общаться лично"
ADMIN_CMD_PRIVATE_ON = "общайся лично"


def _auth_required_text():
    return translate(
        "auth_required",
        commands=" OR ".join(
            [
                f"`/{c} <{translate('password')}>`"
                for c in settings.searcharr_start_command_aliases
            ]
        ),
    )


def _is_group(message: Message) -> bool:
    return message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)


def _is_private(message: Message) -> bool:
    return message.chat.type == ChatType.PRIVATE


async def _bot_identity(message: Message):
    me = await message.bot.get_me()
    return me


async def is_addressed_to_bot(message: Message) -> bool:
    """True if the message mentions the bot or replies to the bot."""
    me = await _bot_identity(message)

    reply = message.reply_to_message
    if reply and reply.from_user and reply.from_user.id == me.id:
        return True

    text = message.text or message.caption or ""
    entities = message.entities or message.caption_entities or []
    username = (me.username or "").lower()

    for ent in entities:
        if ent.type == "mention" and username:
            mention = text[ent.offset : ent.offset + ent.length].lstrip("@").lower()
            if mention == username:
                return True
        if ent.type == "text_mention" and ent.user and ent.user.id == me.id:
            return True

    # Fallback: plain @username in text
    if username and f"@{username}".lower() in text.lower():
        return True

    return False


def strip_bot_mentions(message: Message, bot_username: str, bot_id: int) -> str:
    """Remove @bot mentions from message text for cleaner AI prompts."""
    text = message.text or ""
    entities = list(message.entities or [])
    for ent in sorted(entities, key=lambda e: e.offset, reverse=True):
        drop = False
        if ent.type == "mention" and bot_username:
            mention = text[ent.offset : ent.offset + ent.length].lstrip("@").lower()
            if mention == bot_username.lower():
                drop = True
        elif (
            ent.type == "text_mention"
            and ent.user
            and ent.user.id == bot_id
        ):
            drop = True
        if drop:
            text = text[: ent.offset] + text[ent.offset + ent.length :]
    if bot_username:
        text = text.replace(f"@{bot_username}", "")
        text = text.replace(f"@{bot_username.lower()}", "")
    return " ".join(text.split()).strip()


def detect_admin_voice_command(text: str):
    """Return preference action key if admin voice phrase is present."""
    normalized = " ".join((text or "").lower().split())
    # Longer / more specific phrases first
    checks = (
        (ADMIN_CMD_PRIVATE_OFF, "private_off"),
        (ADMIN_CMD_PRIVATE_ON, "private_on"),
        (ADMIN_CMD_MENTION_ONLY, "mention_only"),
        (ADMIN_CMD_LISTEN_ALL, "listen_all"),
    )
    for phrase, action in checks:
        if phrase in normalized:
            return action
    return None


def apply_admin_action(chat_id: int, action: str) -> str:
    """Apply preference change; return human description for AI prompt."""
    if action == "mention_only":
        set_group_mode(chat_id, MODE_MENTION_ONLY)
        return (
            "В этой группе отвечать только когда к боту обращаются "
            "(@упоминание или ответ на сообщение бота)."
        )
    if action == "listen_all":
        set_group_mode(chat_id, MODE_LISTEN_ALL)
        return (
            "В этой группе анализировать сообщения и участвовать в разговоре "
            "без обязательного обращения."
        )
    if action == "private_off":
        set_private_enabled(False)
        return "Личные сообщения отключены: AI общается только в группах."
    if action == "private_on":
        set_private_enabled(True)
        return "Личные сообщения включены: AI снова может общаться в ЛС."
    return "Настройки не изменились."


def context_key_for(message: Message) -> str:
    if _is_private(message):
        return f"user:{message.from_user.id}"
    return f"chat:{message.chat.id}"


async def _reply_ai(
    message: Message, app, context_key: str, prompt: str, allow_skip=False
):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )
    try:
        answer, category, model_id = await app.ai.chat_routed(context_key, prompt)
    except Exception as e:
        logger.error(f"AI API error: {e}")
        await message.answer(translate("ai_error"))
        return

    normalized = (answer or "").strip()
    if allow_skip and normalized.upper() in (
        "SKIP",
        "[SKIP]",
        "NO",
        "НЕТ",
        "-",
        "—",
        "…",
        "...",
    ):
        return

    if getattr(settings, "ai_announce_route", False):
        await message.answer(
            translate(
                "ai_route_announce",
                category=category,
                model=model_id,
            )
        )

    try:
        await message.answer(normalized, parse_mode="Markdown")
    except TelegramBadRequest:
        await message.answer(normalized)


async def ai_command(message: Message, command: CommandObject, app):
    """Handle /ai [reset|clear] — greet and optionally reset context."""
    if not app.ai or not app.ai.enabled:
        await message.answer(translate("ai_disabled"))
        return

    if not authenticated(message.from_user.id):
        await message.answer(_auth_required_text())
        return

    if _is_private(message) and not is_private_enabled():
        await message.answer(translate("ai_private_disabled"))
        return

    key = context_key_for(message)
    args = (command.args or "").strip().lower()
    if args in ("reset", "clear", "new", "сброс"):
        app.ai.clear_context(key)
        await message.answer(translate("ai_context_cleared"))
        return

    app.ai.clear_context(key)
    await message.answer(translate("ai_welcome"))


async def ai_free_text(message: Message, app):
    """AI free-text + admin voice commands in groups/private."""
    if not app.ai or not app.ai.enabled:
        return
    if not message.text or not message.from_user:
        return
    if message.from_user.is_bot:
        return

    auth_level = authenticated(message.from_user.id)
    if not auth_level:
        return

    me = await _bot_identity(message)
    addressed = await is_addressed_to_bot(message)
    clean_text = strip_bot_mentions(message, me.username or "", me.id)
    # If strip removed everything but there was a reply-to-bot, keep original minus /
    if not clean_text and addressed:
        clean_text = (message.text or "").strip()

    # --- Admin voice commands (group + addressed + admin) ---
    if _is_group(message) and addressed and auth_level == 2:
        action = detect_admin_voice_command(clean_text or message.text or "")
        if action:
            description = apply_admin_action(message.chat.id, action)
            logger.info(
                f"Admin AI prefs change by [{message.from_user.id}] "
                f"chat={message.chat.id} action={action}"
            )
            prompt = (
                "Администратор только что изменил режим работы бота. "
                f"Применённое правило: {description} "
                "Подтверди коротко и по-человечески, что понял инструкцию и "
                "будешь так действовать. Не выдумывай других настроек. "
                f"Сообщение администратора: {clean_text or message.text}"
            )
            await _reply_ai(message, app, context_key_for(message), prompt)
            return

    # --- Private chat gate ---
    if _is_private(message):
        if not is_private_enabled():
            return
        if not clean_text:
            return
        await _reply_ai(
            message, app, context_key_for(message), clean_text
        )
        return

    # --- Group chat gates ---
    if _is_group(message):
        mode = get_group_mode(message.chat.id)
        if mode == MODE_MENTION_ONLY and not addressed:
            return
        if mode == MODE_LISTEN_ALL:
            # Always analyze authenticated users' messages
            pass
        if not clean_text and not addressed:
            return
        if not clean_text:
            return

        allow_skip = False
        prompt = clean_text
        if mode == MODE_LISTEN_ALL and not addressed:
            allow_skip = True
            prompt = (
                "Сообщение в групповом чате (ты слушаешь и анализируешь разговор). "
                "Если можешь быть полезен по фильмам/сериалам/боту — ответь кратко. "
                "Если вмешиваться не нужно — ответь ровно SKIP и ничего больше. "
                f"Текст: {clean_text}"
            )

        await _reply_ai(
            message,
            app,
            context_key_for(message),
            prompt,
            allow_skip=allow_skip,
        )


def register_ai_handlers(router, app):
    """Attach AI command + free-text handlers to a router."""
    aliases = getattr(settings, "ai_command_aliases", None) or ["ai"]
    app.logger.debug(f"Registering AI commands: {aliases}")
    router.message.register(ai_command, Command(*aliases))

    # Plain text only — /movie /series stay on Command handlers (with or without @bot)
    router.message.register(
        ai_free_text,
        F.text,
        ~F.text.startswith("/"),
    )
