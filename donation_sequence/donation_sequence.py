import os
import time
import logging
import random

from utils.image_utils import ImageUtils
from utils.adb_utils import ADBUtils
from utils.main_utils import click_button, wait_for_ui_stabilization

class DonationSequence:
    def __init__(self, debug_mode=True):
        self.adb = ADBUtils()
        self.image = ImageUtils(debug_mode=debug_mode)
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")
        
        # Validate required images
        self.required_images = [
            "back_button.png",
            "clan_chat.png",
            "donation_request.png",
            "donate_button.png" 
        ]
        
        self._validate_images()
        
        logging.info("\n" + "="*50)
        logging.info("DONATION SEQUENCE INITIALIZED")
        logging.info("="*50)

    def _validate_images(self):
        """Validate that all required images exist."""
        missing_images = []
        for image in self.required_images:
            image_path = os.path.join(self.image_folder, image)
            if not os.path.exists(image_path):
                missing_images.append(image)
        
        if missing_images:
            error_msg = "❌ Missing required images in donation_sequence/images/:\n"
            for img in missing_images:
                error_msg += f"  - {img}\n"
            error_msg += "Please add these images to continue."
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)

    def navigate_to_clan(self):
        """Navigate to the clan chat screen."""
        logging.info("\n" + "-"*40)
        logging.info("NAVIGATING TO CLAN CHAT")
        logging.info("-"*40)

        # First check if we're already in clan chat by looking for back button
        if self.image.detect_image(self.adb, self.image_folder, "back_button.png"):
            logging.info("Already in clan chat (back button detected)")
            return True

        # Try to find and click clan chat button
        if not click_button(self.image, self.adb, self.image_folder, "clan_chat.png"):
            logging.error("❌ Failed to find clan chat button")
            return False

        # Wait for clan chat to load and verify we're there
        time.sleep(2)
        if self.image.detect_image(self.adb, self.image_folder, "back_button.png"):
            logging.info("Successfully navigated to clan chat")
            return True
            
        logging.error("❌ Failed to verify clan chat navigation")
        return False

    def check_donation_requests(self):
        """Check for donation requests in clan chat."""
        logging.info("Checking for donation requests...")
        
        # Take a new screenshot for verification
        if not self.adb.take_screenshot("donation_check.png"):
            logging.error("❌ Failed to take screenshot for donation check")
            return False
            
        # Look for donation request indicators
        if self.image.detect_image(self.adb, self.image_folder, "donation_request.png"):
            logging.info("✅ Found donation request")
            return True
            
        logging.info("No donation requests found")
        return False

    def donate_troops(self):
        """Donate troops to clan members."""
        logging.info("\n" + "-"*40)
        logging.info("DONATING TROOPS")
        logging.info("-"*40)

        # Take a new screenshot for donation button check
        if not self.adb.take_screenshot("donation_screen.png"):
            logging.error("❌ Failed to take screenshot for donation")
            return False

        # Click on the donation request
        if not click_button(self.image, self.adb, self.image_folder, "donation_request.png"):
            logging.error("❌ Failed to find donation request")
            return False

        time.sleep(1)

        # Take another screenshot to verify donation button
        if not self.adb.take_screenshot("donate_button_check.png"):
            logging.error("❌ Failed to take screenshot for donate button check")
            return False

        # Click donate button
        if not click_button(self.image, self.adb, self.image_folder, "donate_button.png"):
            logging.error("❌ Failed to find donate button")
            return False

        time.sleep(1)

        logging.info("✅ Successfully donated troops")
        return True

    def return_to_home(self):
        """Return to the home screen."""
        logging.info("Returning to home screen...")
        
        # First check if we're already at home
        if self.image.detect_image(self.adb, self.image_folder, "clan_chat.png"):
            logging.info("Already at home screen")
            return True
        
        # Try clicking back button
        if not click_button(self.image, self.adb, self.image_folder, "back_button.png"):
            logging.error("❌ Failed to find back button")
            return False

        time.sleep(1)
        
        # Verify we're at home
        if self.image.detect_image(self.adb, self.image_folder, "clan_chat.png"):
            logging.info("Successfully returned to home screen")
            return True
            
        logging.error("❌ Failed to verify return to home")
        return False

    def execute_donation_cycle(self):
        """Execute a complete donation cycle."""
        try:
            # Navigate to clan chat
            if not self.navigate_to_clan():
                return False

            # Check for donation requests
            if not self.check_donation_requests():
                logging.info("No donation requests to fulfill")
                return self.return_to_home()

            # Donate troops
            if not self.donate_troops():
                return self.return_to_home()

            # Return to home
            return self.return_to_home()

        except Exception as e:
            logging.error(f"❌ Error during donation cycle: {str(e)}")
            return False 