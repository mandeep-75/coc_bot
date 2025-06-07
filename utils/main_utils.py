import logging
import time
import random
import os

def click_button(image_utils, adb, image_folder, button_name, confidence_threshold: float = 0.6, attempts: int = 3, log_prefix: str = "") -> bool:
    """Click a button with a specified number of attempts, using improved image_utils method."""
    for attempt in range(attempts):
        logging.info(f"{log_prefix}Attempting to click '{button_name}' (attempt {attempt + 1}/{attempts})")
        if image_utils.find_and_click_image(adb, image_folder, button_name, confidence_threshold, log_prefix=log_prefix):
            logging.info(f"{log_prefix}✅ Successfully clicked '{button_name}'")
            return True
        else:
            logging.warning(f"{log_prefix}⚠️ Could not find '{button_name}' on attempt {attempt + 1}")
            time.sleep(0.5)  # Short delay before retrying
    return False

def wait_for_ui_stabilization(seconds=1):
    """Wait for UI stabilization."""
    logging.info(f"⏳ Waiting for UI stabilization for {seconds} seconds...")
    time.sleep(seconds)

def check_game_state(adb, image_utils, image_folder):
    """Check if the game is in the expected state."""
    logging.info("\n" + "-"*40)
    logging.info("CHECKING GAME STATE")
    logging.info("-"*40)
    
    home_anker = os.path.join(image_folder, "home_anker.png")
    
    if not adb.take_screenshot("screen.png"):
        logging.error("❌ Failed to take screenshot while checking game state")
        return False
        
    home_anker_pos = image_utils.find_image("screen.png", home_anker)

    if home_anker_pos:
        logging.info("✅ Game is in the expected state")
        return True

    logging.warning("❌ Game is not in expected state")
    return False 