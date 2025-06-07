import os
import time
import random
import logging

from utils.image_utils import ImageUtils
from utils.adb_utils import ADBUtils 
from utils.main_utils import click_button, wait_for_ui_stabilization, check_game_state

class StartingSequence:
    def __init__(self, debug_mode=True):
        self.adb = ADBUtils()
        self.image = ImageUtils(debug_mode=debug_mode)
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")
        logging.info("\n" + "="*50)
        logging.info("STARTING SEQUENCE INITIALIZED")
        logging.info("="*50)

    def check_game_state(self):
        """Check if the game is in the expected state."""
        logging.info("\n" + "-"*40)
        logging.info("CHECKING GAME STATE")
        logging.info("-"*40)
        
        home_anker = os.path.join(self.image_folder, "home_anker.png")
        
        if not self.adb.take_screenshot("screen.png"):
            logging.error("❌ Failed to take screenshot while checking game state")
            return False
            
        home_anker_pos = self.image.find_image("screen.png", home_anker)

        if home_anker_pos:
            logging.info("✅ Game is in the expected state")
            return True

        logging.warning("❌ Game is not in expected state")
        return False

    def collect_resources(self):
        """Collect resources by clicking on resource icons."""
        logging.info("\n" + "="*50)
        logging.info("STARTING RESOURCE COLLECTION")
        logging.info("="*50)
        
        if not self.check_game_state():
            logging.warning("❌ Game not in expected state, cannot collect resources")
            return False
      
        resources = ["gold.png", "elixir.png", "dark_elixir.png"]
        
        logging.info("\n" + "-"*40)
        logging.info("COLLECTING RESOURCES")
        logging.info("-"*40)
        
        resource_count = 0
        for resource in resources:
            logging.info(f"Attempting to collect {resource}...")
            if self.image.find_and_click_image(self.adb, self.image_folder, resource):
                logging.info(f"✅ Successfully clicked on {resource}")
                resource_count += 1
                time.sleep(random.uniform(1, 2))  # Mimic human delay
            else:
                logging.info(f"⏭️ {resource} not found or could not be clicked")

        logging.info("\n" + "-"*40)
        logging.info(f"RESOURCE COLLECTION COMPLETED: {resource_count}/{len(resources)} resources collected")
        logging.info("-"*40)
        return True

    def is_home_screen(self):
        logging.info("Checking if we are on the home screen...")
        
        if not self.adb.take_screenshot("screen.png"):
            logging.error("❌ Failed to take screenshot while checking home screen")
            return False
            
        # Check for home screen indicators
        for marker in ["home_anker.png"]:
            if self.image.detect_image(self.adb, self.image_folder, marker):
                logging.info(f"✅ Home screen detected using {marker}")
                return True
        
        logging.warning("❌ Not on home screen")
        return False

    def navigate_to_home(self, max_attempts=5):
        """Attempt to navigate back to the home screen"""
        logging.info("\n" + "-"*40)
        logging.info("NAVIGATING TO HOME SCREEN")
        logging.info("-"*40)
        
        # First check if already on home screen
        if self.is_home_screen():
            return True
        
        # Try clicking UI elements that can lead back to home
        for _ in range(max_attempts):
            # Take a screenshot
            if not self.adb.take_screenshot("screen.png"):
                continue
            
            # Check for buttons that can help return to home
            buttons = ["close.png","end_battle.png","return_home.png","back_anchor.png"]
            
            clicked = False
            for button in buttons:
                if self.image.find_and_click_image(self.adb, self.image_folder, button):
                    logging.info(f"✅ Clicked {button} to return home")
                    clicked = True
                    time.sleep(1.5)
                    break
            
            # If we didn't click anything, try a special technique - click top left corner
            # if not clicked:
            #     logging.info("Trying to centre screen ")
            #     self.adb.humanlike_click(50, 50)  # Top left is often a back button
            #     time.sleep(1.5)
            
            # Check if we reached home
            if self.is_home_screen():
                logging.info("✅ Successfully navigated to home screen")
                return True
        
        logging.error("❌ Failed to navigate to home screen after multiple attempts")
        return False
