
# =============================================================================
# FLOW CONFIGURATION - Control which tasks run
# =============================================================================
# Set to True/False to enable/disable each task
# The bot will run tasks in the order defined here
FLOW_CONFIG = {
    "collect_gold": True,
    "collect_elixir": True,
    "collect_dark_elixir": True,
    "find_match": True,
    "search_for_base": True,
    "deploy_troops": True,
    "deploy_heroes": True,
    "deploy_spells": True,
    "trigger_abilities": True,
    "return_home": True,
}

# =============================================================================
# CONFIGURATION
# =============================================================================

# Discord Webhook URL for notifications (leave empty to disable)
DISCORD_WEBHOOK_URL = ""

# Screenshot filename (used for all template matching)
SCREENSHOT_NAME = "screen.png"

# Log file for session tracking
LOG_FILE = "bot_session_log.txt"

# Random offset ranges to make clicks appear more human-like
# Higher values = more variation in tap position
RANDOM_OFFSET = 3         # For troop deployments
RANDOM_OFFSET_HEROES = 3  # For hero deployments
RANDOM_OFFSET_SPELLS = 25 # For spell deployments (larger area)

# Resource thresholds for base selection
# Bot will attack bases that meet ALL of these minimums:
GOLD_THRESHOLD =500_000        # Minimum gold required
ELIXIR_THRESHOLD = 500_000      # Minimum elixir required
DARK_ELIXIR_THRESHOLD = 0         # Minimum dark elixir required
MAX_TROPHIES_ATTACK_THRESHOLD = 30  # Reserved for future trophy-based filtering

# =============================================================================
# TIMEOUTS (in seconds)
# =============================================================================
BASE_SEARCH_TIMEOUT = 120   # Maximum time to spend searching for a suitable base
RETURN_HOME_TIMEOUT = 210   # Maximum time to wait for return home button after battle

# =============================================================================
# UI TEMPLATE FOLDERS
# =============================================================================
# Path to builder menu button template (for future use)
BUILD_MENU_BUTTON_FOLDER = "ui_main_base/builder_menu_button"

# =============================================================================
# DEPLOYMENT COORDINATES
# =============================================================================
# Number of troops to deploy per attack (should match your army camp capacity)
TROOP_COUNT = 28

TROOP_LOCATIONS = [
    (173, 380), (198, 395), (220, 413), (252, 438), (293, 464),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
    (227, 258), (256, 230), (293, 464),
]

SPELL_LOCATIONS = [
    (588, 272), (494, 395), (583, 205), (636, 395), (632, 500),
]

HERO_LOCATIONS = [
    (149, 320), (194, 379), (214, 261), (157, 325), (214, 261),
]
