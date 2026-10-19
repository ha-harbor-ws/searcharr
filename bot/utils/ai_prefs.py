"""
Persistent AI behaviour preferences (group mode + private chat).
"""
from bot.utils.database import execute_insert, execute_query, get_connection, DBLOCK
from bot.utils.log import set_up_logger

logger = set_up_logger("ai_prefs")

# Global key in ai_kv
KEY_PRIVATE_ENABLED = "private_enabled"

# Per-chat group modes
MODE_MENTION_ONLY = "mention_only"
MODE_LISTEN_ALL = "listen_all"

DEFAULT_PRIVATE_ENABLED = True
DEFAULT_GROUP_MODE = MODE_MENTION_ONLY


def ensure_ai_prefs_schema():
    """Create AI prefs tables if missing."""
    con, cur = get_connection()
    queries = [
        """CREATE TABLE IF NOT EXISTS ai_kv (
            key text primary key,
            value text not null
        );""",
        """CREATE TABLE IF NOT EXISTS ai_chat_prefs (
            chat_id integer primary key,
            group_mode text not null
        );""",
    ]
    try:
        with DBLOCK:
            for q in queries:
                cur.execute(q)
            con.commit()
    finally:
        con.close()


def get_kv(key: str, default: str = "") -> str:
    rows = execute_query("SELECT value FROM ai_kv WHERE key=?;", (key,))
    if not rows:
        return default
    return rows[0]["value"]


def set_kv(key: str, value: str) -> bool:
    return execute_insert(
        "INSERT OR REPLACE INTO ai_kv (key, value) VALUES (?, ?);",
        (key, value),
    )


def is_private_enabled() -> bool:
    raw = get_kv(KEY_PRIVATE_ENABLED, "1" if DEFAULT_PRIVATE_ENABLED else "0")
    return raw not in ("0", "false", "False", "")


def set_private_enabled(enabled: bool) -> bool:
    return set_kv(KEY_PRIVATE_ENABLED, "1" if enabled else "0")


def get_group_mode(chat_id: int) -> str:
    rows = execute_query(
        "SELECT group_mode FROM ai_chat_prefs WHERE chat_id=?;",
        (chat_id,),
    )
    if not rows:
        return DEFAULT_GROUP_MODE
    mode = rows[0]["group_mode"]
    if mode not in (MODE_MENTION_ONLY, MODE_LISTEN_ALL):
        return DEFAULT_GROUP_MODE
    return mode


def set_group_mode(chat_id: int, mode: str) -> bool:
    if mode not in (MODE_MENTION_ONLY, MODE_LISTEN_ALL):
        raise ValueError(f"Invalid group mode: {mode}")
    return execute_insert(
        "INSERT OR REPLACE INTO ai_chat_prefs (chat_id, group_mode) VALUES (?, ?);",
        (chat_id, mode),
    )
