"""
Searcharr
Sonarr & Radarr Telegram Bot
By Todd Roberts
https://github.com/toddrob99/searcharr
"""

# Searcharr Bot
searcharr_password = ""  # Used to authenticate as a regular user to add series/movies
searcharr_admin_password = ""  # Used to authenticate as admin to manage users
searcharr_language = "en-us"  # yml file in the lang folder
searcharr_start_command_aliases = ["start"]  # Override /start command
searcharr_help_command_aliases = ["help"]  # Override /help command
searcharr_users_command_aliases = ["users"]  # Override /users command

# Telegram
tgram_token = ""
# Optional Local Bot API server root, e.g. "http://127.0.0.1:8081"
# Leave empty to use the official Telegram API (https://api.telegram.org).
tg_local_api_url = ""
# Set True if the local Bot API server is started with --local
tg_local_mode = False

# Sonarr
sonarr_enabled = True
sonarr_url = ""  # http://192.168.0.100:8989
sonarr_api_key = ""
sonarr_quality_profile_id = ["HD - 720p/1080p"]  # can be name or id value - include multiple to allow the user to choose
sonarr_add_monitored = True
sonarr_search_on_add = True
sonarr_tag_with_username = True
sonarr_forced_tags = []  # e.g. ["searcharr", "friends-and-family"] - leave empty for none
sonarr_allow_user_to_select_tags = True
sonarr_user_selectable_tags = []  # e.g. ["custom-tag-1", "custom-tag-2"] - leave empty to let user choose from all tags in Sonarr
sonarr_series_command_aliases = ["series"]  # e.g. ["series", "tv", "t"]
sonarr_series_paths = []  # e.g. ["/tv", "/anime"] - can be full path or id value - leave empty to enable all
sonarr_season_monitor_prompt = False  # False - always monitor all seasons; True - prompt user to select from All, First, or Latest season(s)

# Radarr
radarr_enabled = True
radarr_url = ""  # http://192.168.0.100:7878
radarr_api_key = ""
radarr_quality_profile_id = ["HD - 720p/1080p"]  # can be name or id value - include multiple to allow the user to choose
radarr_add_monitored = True
radarr_search_on_add = True
radarr_tag_with_username = True
radarr_forced_tags = []  # e.g. ["searcharr", "friends-and-family"] - leave empty for none
radarr_allow_user_to_select_tags = True
radarr_user_selectable_tags = []  # e.g. ["custom-tag-1", "custom-tag-2"] - leave empty to let user choose from all tags in Radarr
radarr_min_availability = "released"  # options: "announced", "inCinemas", "released"
radarr_movie_command_aliases = ["movie"]  # e.g. ["movie", "mv", "m"]
radarr_movie_paths = []  # e.g. ["/movies", "/other-movies"] - can be full path or id value - leave empty to enable all

# AI chat (OpenAI-compatible; defaults tuned for OpenRouter FREE models)
ai_enabled = False
ai_api_key = ""  # OpenRouter free API key
# https://openrouter.ai is normalized to .../api/v1 automatically
ai_base_url = "https://openrouter.ai/api/v1"
# Fallback model if every model in the chosen pool fails with HTTP 5xx
# (also used to fill ai_models_general when that list is empty)
ai_model = "google/gemma-4-31b:free"
ai_system_prompt = ""  # empty = built-in HarborTV media assistant prompt
ai_max_context = 10  # max messages kept in memory per user/chat (incl. system)
# Persist chat history to disk (survives restart); file lives under data/ by default
ai_context_persist = True
ai_context_save_interval = 60  # seconds between autosaves
ai_context_file = ""  # empty = data/ai_contexts.json; or relative/absolute path
ai_command_aliases = ["ai"]  # /ai — start/reset chat; free text continues dialogue

# Model router (dispatcher picks light / general / complex, then a model from the pool)
ai_router_enabled = True
ai_router_model = "nvidia/nemotron-3.5-lightning:free"  # fast free classifier
ai_router_timeout = 5.0  # seconds; on timeout/error fallback to general
ai_announce_route = False  # if True, briefly show chosen category/model before answer
# Free OpenRouter pools — add more IDs to each list for round-robin + failover
ai_models_light = [
    "openrouter/free",  # more reliable than some :free specialists
]
ai_models_general = [
    "openrouter/free",
]
ai_models_complex = [
    "openrouter/free",
]

# Retries / error replies (OpenRouter 429, 402, etc.)
ai_max_retries = 3  # attempts per model on 429 / transient 5xx
ai_retry_delay = 4  # base pause seconds before first retry
ai_retry_backoff = 2  # multiply delay after each retry
ai_request_timeout = 60  # seconds per model HTTP call (OpenRouter)
ai_error_rate_limit = (
    "⚠️ Извините, сейчас сервер слишком занят (превышен лимит запросов). "
    "Пожалуйста, повторите ваш вопрос через 15-20 секунд."
)
ai_error_no_credits = (
    "❌ К сожалению, на сегодня бесплатные лимиты или кредиты аккаунта "
    "полностью исчерпаны. Бот возобновит работу позже."
)
ai_error_api = "Произошла техническая ошибка на стороне нейросети. Попробуйте позже."
ai_error_generic = (
    "Что-то пошло не так при генерации ответа. Пожалуйста, попробуйте еще раз."
)

# Group AI prefs (changed live by admin text commands when addressing the bot):
# "не влезай в разговор" / "поговори с нами" / "хватит общаться лично" / "общайся лично"
# Runtime state is stored in data/searcharr.db (ai_kv, ai_chat_prefs).
