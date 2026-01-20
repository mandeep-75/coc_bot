
# =============================================================================
# CONFIGURATION
# =============================================================================

# Discord Webhook URL (Leave empty to disable)
DISCORD_WEBHOOK_URL = ""

# Screenshot file used everywhere
SCREENSHOT_NAME = "screen.png"

# Log file for tracking progress
LOG_FILE = "bot_session_log.txt"

# Random offsets to make clicks look human
RANDOM_OFFSET = 3
RANDOM_OFFSET_HEROES = 3
RANDOM_OFFSET_SPELLS = 25

# Resource Thresholds for finding a match
GOLD_THRESHOLD = 1_000_000
ELIXIR_THRESHOLD = 1_000_000
DARK_ELIXIR_THRESHOLD = 0
MAX_TROPHIES_ATTACK_THRESHOLD = 30  # Currently unused

# UI template folders
BUILD_MENU_BUTTON_FOLDER = "ui_main_base/builder_menu_button"

# Wall Upgrades
WALL_UPGRADES_ENABLED = True

# =============================================================================
# DEPLOYMENT COORDINATES
# =============================================================================
TROOP_LOCATIONS = [
    (173, 380), (198, 395), (220, 413), (252, 438), (293, 464),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
    (227, 258), (256, 230), (293, 464)
]

SPELL_LOCATIONS = [
    (588, 272), (494, 395), (583, 205), (636, 395), (632, 500)
]

HERO_LOCATIONS = [
    (149, 320), (194, 379), (214, 261), (157, 325), (214, 261)
]
