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
    if not hasattr(settings, "ai_router_model") or not getattr(
        settings, "ai_router_model", ""
    ):
        settings.ai_router_model = "nvidia/nemotron-3.5-lightning:free"
    if not hasattr(settings, "ai_router_timeout"):
        settings.ai_router_timeout = 5.0
    try:
        settings.ai_router_timeout = max(
            1.0, float(settings.ai_router_timeout)
        )
    except (TypeError, ValueError):
        settings.ai_router_timeout = 5.0
    if not hasattr(settings, "ai_announce_route"):
        settings.ai_announce_route = False
    if not hasattr(settings, "ai_models_light"):
        settings.ai_models_light = ["nvidia/nemotron-3-super:free"]
    if not hasattr(settings, "ai_models_general"):
        settings.ai_models_general = (
            [settings.ai_model]
            if settings.ai_model
            else ["google/gemma-4-31b:free"]
        )
    if not hasattr(settings, "ai_models_complex"):
        settings.ai_models_complex = ["dots-studio/dots-3-note-preview:free"]

    if not hasattr(settings, "ai_max_retries"):
        settings.ai_max_retries = 3
    try:
        settings.ai_max_retries = max(1, int(settings.ai_max_retries))
    except (TypeError, ValueError):
        settings.ai_max_retries = 3
    if not hasattr(settings, "ai_retry_delay"):
        settings.ai_retry_delay = 4
    try:
        settings.ai_retry_delay = max(0.5, float(settings.ai_retry_delay))
    except (TypeError, ValueError):
        settings.ai_retry_delay = 4.0
    if not hasattr(settings, "ai_retry_backoff"):
        settings.ai_retry_backoff = 2
    try:
        settings.ai_retry_backoff = max(1.0, float(settings.ai_retry_backoff))
    except (TypeError, ValueError):
        settings.ai_retry_backoff = 2.0
    if not hasattr(settings, "ai_request_timeout"):
        settings.ai_request_timeout = 60
    try:
        settings.ai_request_timeout = max(
            5.0, float(settings.ai_request_timeout)
        )
    except (TypeError, ValueError):
        settings.ai_request_timeout = 60.0

    _default_errors = {
        "ai_error_rate_limit": (
            "⚠️ Извините, сейчас сервер слишком занят (превышен лимит запросов). "
            "Пожалуйста, повторите ваш вопрос через 15-20 секунд."
        ),
        "ai_error_no_credits": (
            "❌ К сожалению, на сегодня бесплатные лимиты или кредиты аккаунта "
            "полностью исчерпаны. Бот возобновит работу позже."
        ),
        "ai_error_api": (
            "Произошла техническая ошибка на стороне нейросети. Попробуйте позже."
        ),
        "ai_error_generic": (
            "Что-то пошло не так при генерации ответа. Пожалуйста, попробуйте еще раз."
        ),
    }
    for key, default in _default_errors.items():
        if not hasattr(settings, key) or not getattr(settings, key):
            setattr(settings, key, default)

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