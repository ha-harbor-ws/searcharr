"""
Searcharr
Sonarr & Radarr Telegram Bot
Text Processing Utilities
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
from aiogram.types import Message

from bot.utils.log import set_up_logger
from config.language import translate as _translate

logger = set_up_logger("text")


def strip_entities(message: Message) -> str:
    """Strip Telegram entities (commands, mentions, etc.) from a message text."""
    text = message.text or ""
    entities = message.entities or []

    entity_texts = [
        text[entity.offset : entity.offset + entity.length] for entity in entities
    ]
    logger.debug(f"Entities in message: {entity_texts}")

    for value in entity_texts:
        text = text.replace(value, "")

    text = text.replace("  ", "").strip()
    logger.debug(
        f"Stripped entities from message [{message.text}]: [{text}]"
    )
    return text


def translate(key, **kwargs):
    """Translate a key using the loaded language data."""
    return _translate(key, **kwargs)
