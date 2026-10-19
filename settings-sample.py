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

# AI chat (OpenAI-compatible: OpenRouter, RouterAI, etc.)
ai_enabled = False
ai_api_key = ""  # OpenRouter (or other OpenAI-compatible) API key
# Default: OpenRouter. Alternatives e.g. "https://routerai.ru/v1"
ai_base_url = "https://openrouter.ai/api/v1"
# Legacy single model (used only if ai_models_general is empty)
ai_model = "deepseek/deepseek-chat"
ai_system_prompt = ""  # empty = built-in HarborTV media assistant prompt
ai_max_context = 10  # max messages kept in memory per user/chat (incl. system)
# Persist chat history to disk (survives restart); file lives under data/ by default
ai_context_persist = True
ai_context_save_interval = 60  # seconds between autosaves
ai_context_file = ""  # empty = data/ai_contexts.json; or relative/absolute path
ai_command_aliases = ["ai"]  # /ai — start/reset chat; free text continues dialogue

# Model router (dispatcher picks light / general / complex, then a model from the pool)
ai_router_enabled = True
ai_router_model = "openai/gpt-4o-mini"  # cheap classifier model
ai_announce_route = False  # if True, briefly show chosen category/model before answer
# Multiple models per tier — round-robin + failover to the next on error
ai_models_light = [
    "qwen/qwen-2.5-72b-instruct",
]
ai_models_general = [
    "deepseek/deepseek-chat",
]
ai_models_complex = [
    "deepseek/deepseek-r1",
]

# Group AI prefs (changed live by admin text commands when addressing the bot):
# "не влезай в разговор" / "поговори с нами" / "хватит общаться лично" / "общайся лично"
# Runtime state is stored in data/searcharr.db (ai_kv, ai_chat_prefs).
