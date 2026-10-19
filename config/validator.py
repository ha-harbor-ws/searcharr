"""
Searcharr
Sonarr & Radarr Telegram Bot
Settings Validator
By Todd Roberts
https://github.com/toddrob99/searcharr
"""
import uuid

from bot.utils.log import set_up_logger
import settings

logger = set_up_logger("config.validator")


def validate_settings():
    """Validate and set defaults for general settings."""
    # Check admin password
    if not hasattr(settings, "searcharr_admin_password"):
        settings.searcharr_admin_password = uuid.uuid4().hex
        logger.warning(
            f'No admin password detected. Please set one in settings.py (searcharr_admin_password="your admin password"). '
            f'Using {settings.searcharr_admin_password} as the admin password for this session.'
        )
        
    # Check user password
    if getattr(settings, "searcharr_password", "") == "":
        logger.warning(
            'Password is blank. This will allow anyone to add series/movies using your bot. '
            'If this is unexpected, set a password in settings.py (searcharr_password="your password").'
        )
        
    # Check command aliases
    for cmd_type in ["start", "help", "users"]:
        setting_name = f"searcharr_{cmd_type}_command_aliases"
        if not hasattr(settings, setting_name):
            setattr(settings, setting_name, [cmd_type])
            logger.warning(
                f'No {setting_name} setting found. Please add {setting_name} to settings.py '
                f'(e.g. {setting_name}=["{cmd_type}"]. Defaulting to ["{cmd_type}"].'
            )
    
    # Check language setting
    if not hasattr(settings, "searcharr_language"):
        settings.searcharr_language = "en-us"
        logger.warning(
            "No searcharr_language setting found. Please add searcharr_language to settings.py "
            '(e.g. searcharr_language="en-us"). Defaulting to "en-us".'
        )

    # Optional Local Telegram Bot API
    if not hasattr(settings, "tg_local_api_url"):
        settings.tg_local_api_url = ""
    if not hasattr(settings, "tg_local_mode"):
        settings.tg_local_mode = False

    # Optional AI chat (OpenAI-compatible aggregator)
    if not hasattr(settings, "ai_enabled"):
        settings.ai_enabled = False
    if not hasattr(settings, "ai_api_key"):
        settings.ai_api_key = ""
    if not hasattr(settings, "ai_base_url") or not getattr(
        settings, "ai_base_url", ""
    ):
        settings.ai_base_url = "https://openrouter.ai/api/v1"
    if not hasattr(settings, "ai_model"):
        settings.ai_model = ""
    if not hasattr(settings, "ai_system_prompt"):
        settings.ai_system_prompt = ""
    if not hasattr(settings, "ai_max_context"):
        settings.ai_max_context = 10
    try:
        settings.ai_max_context = max(2, int(settings.ai_max_context))
    except (TypeError, ValueError):
        settings.ai_max_context = 10
    if not hasattr(settings, "ai_context_persist"):
        settings.ai_context_persist = True
    if not hasattr(settings, "ai_context_save_interval"):
        settings.ai_context_save_interval = 60
    try:
        settings.ai_context_save_interval = max(
            5, int(settings.ai_context_save_interval)
        )
    except (TypeError, ValueError):
        settings.ai_context_save_interval = 60
    if not hasattr(settings, "ai_context_file"):
        settings.ai_context_file = ""
    if not hasattr(settings, "ai_command_aliases"):
        settings.ai_command_aliases = ["ai"]
    if not hasattr(settings, "ai_router_enabled"):
        settings.ai_router_enabled = True
    if not hasattr(settings, "ai_router_model"):
        settings.ai_router_model = "openai/gpt-4o-mini"
    if not hasattr(settings, "ai_announce_route"):
        settings.ai_announce_route = False
    if not hasattr(settings, "ai_models_light"):
        settings.ai_models_light = ["qwen/qwen-2.5-72b-instruct"]
    if not hasattr(settings, "ai_models_general"):
        settings.ai_models_general = (
            [settings.ai_model] if settings.ai_model else ["deepseek/deepseek-chat"]
        )
    if not hasattr(settings, "ai_models_complex"):
        settings.ai_models_complex = ["deepseek/deepseek-r1"]

    # Normalize model pools to lists of strings
    for pool_name in (
        "ai_models_light",
        "ai_models_general",
        "ai_models_complex",
    ):
        raw = getattr(settings, pool_name, [])
        if isinstance(raw, str):
            setattr(settings, pool_name, [raw] if raw.strip() else [])
        else:
            setattr(
                settings,
                pool_name,
                [str(x).strip() for x in (raw or []) if str(x).strip()],
            )

    has_models = any(
        getattr(settings, n, None)
        for n in ("ai_models_light", "ai_models_general", "ai_models_complex")
    ) or bool(getattr(settings, "ai_model", ""))
    if settings.ai_enabled and not (
        settings.ai_api_key and settings.ai_base_url and has_models
    ):
        logger.warning(
            "ai_enabled=True but ai_api_key / ai_base_url / model pools are incomplete."
        )