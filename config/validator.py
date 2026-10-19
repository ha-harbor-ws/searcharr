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