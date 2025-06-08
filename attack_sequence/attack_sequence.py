import os
import logging
import time
import random
import cv2
import numpy as np
from utils.adb_utils import ADBUtils
from utils.image_utils import ImageUtils
from utils.debug_utils import DebugVisualizer
from search_sequence.search_sequence import SearchSequence
from utils.main_utils import click_button, wait_for_ui_stabilization

class AttackSequence:
    def __init__(self, target_percentage=50, debug_mode=True, search_sequence=None):
        """
        Initialize the attack sequence with a target destruction percentage.

        Args:
            target_percentage: Minimum destruction percentage to achieve (default: 50 for one star)
            debug_mode: Whether to enable debug visualization
            search_sequence: The search sequence instance to use for finding bases
        """
        self.adb = ADBUtils()
        self.image = ImageUtils(debug_mode=debug_mode)
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")
        self.target_percentage = target_percentage
        self.search_sequence = search_sequence
        # Initialize deployment locations dictionary
        self.deployment_locations = {}
        self.debugger = DebugVisualizer(debug_mode=debug_mode)

    def execute_attack(self, max_duration=10):
        """
        Execute a simplified attack assuming we're already at the attack screen.

        Returns:
            bool: True to indicate attack was completed
        """
        logging.info("\n" + "=" * 50)
        logging.info("EXECUTING ATTACK")
        logging.info("=" * 50)

        # First prepare troop deployment (identify troops, spells, etc.)
        if not self.prepare_deployment():
            logging.error("❌ Failed to prepare deployment - aborting attack")
            return False

        # Deploy all troops in sequence
        if not self.deploy_all():
            logging.error("❌ Failed to deploy troops - aborting attack")
            return False

        # Wait a shorter time for deployment animations
        logging.info("Waiting for deployment animations to complete...")
        time.sleep(1.5)  # Reduced from 3 seconds

        # Try to find and click the return home button
        max_attempts = 30

        for attempt in range(max_attempts):
            logging.info(f"Attempt {attempt + 1}/{max_attempts}: Looking for return home button...")
            wait_for_ui_stabilization(10)  
            # Check if return home button is detected with confidence ≥ 0.7
            if self.image.detect_image(self.adb, self.image_folder, "return_home.png", confidence_threshold=0.7):
                logging.info("🏠 Return home button found. Running normal exit sequence.")
                if self.image.find_and_click_image(self.adb, self.image_folder, "return_home.png", confidence_threshold=0.7):
                    logging.info("✅ Found and clicked return_home.png")
                    time.sleep(1)
                    logging.info("Attack sequence completed.")
                    return True

            logging.info("Return home button not found, retrying...")
            time.sleep(0.5)  # Reduced from 1 second

        logging.warning("⚠️ Could not find return home button after multiple attempts.")
        logging.info("Attack sequence completed with issues.")
        return False

    def is_home_screen(self):
        """Check if the game is currently on the home screen"""
        if not self.adb.take_screenshot("screen.png"):
            logging.error("❌ Failed to take screenshot while checking home screen")
            return False

        # Check for home screen indicators
        for marker in ["home_anchor.png"]:
            if self.image.detect_image(self.adb, self.image_folder, marker):
                logging.info(f"✅ Home screen detected using {marker}")
                return True

        logging.info("⏳ Not on home screen yet")
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
            buttons = ["close.png", "back_anchor.png", "return_home.png"]

            clicked = False
            for button in buttons:
                if self.image.find_and_click_image(self.adb, self.image_folder, button):
                    logging.info(f"✅ Clicked {button} to return home")
                    clicked = True
                    wait_for_ui_stabilization(1.5)
                    break

            # If we didn't click anything, try a special technique - click top left corner
            if not clicked:
                logging.info("Trying to click top-left area (often has home/back button)")
                self.adb.humanlike_click(50, 50)  # Top left is often a back button
                wait_for_ui_stabilization(1.5)

            # Check if we reached home
            if self.is_home_screen():
                logging.info("✅ Successfully navigated to home screen")
                return True

        logging.error("❌ Failed to navigate to home screen after multiple attempts")
        return False

    def prepare_deployment(self):
        """
        Prepare deployment by detecting troops, spells and heroes from the attack screen.
        Uses reference images to locate troops in the selection bar at the bottom of the screen.
        Optimized with faster detection methods.
        """
        logging.info("\n" + "-"*40)
        logging.info("PREPARING TROOP DEPLOYMENT")
        logging.info("-"*40)

        # Take a screenshot for troop detection
        logging.info("Taking screenshot for troop detection...")
        if not self.adb.take_screenshot("screen.png"):
            logging.error("❌ Failed to take screenshot for deployment preparation")
            return False


 

        elements_to_detect = {
            "super_minion": ("super_minion.png", 25),
            "ice_spell": ("spell_ice.png", 1),
            "rage_spell": ("spell.png", 5),
            "hero_5": ("hero_5.png", 1),
            "hero_4": ("hero_4.png", 1),
            "hero_3": ("hero_3.png", 1),
            "hero_2": ("hero_2.png", 1),
            "hero_1": ("hero_1.png", 1),
        }

        # Clear previous deployment locations
        self.deployment_locations = {}
        detected_count = 0
        hero_count = 0

        try:
            # Load screenshot for visualization
            logging.info("Loading screenshot for visualization...")
            screenshot = cv2.imread("screen.png")
            if screenshot is None:
                logging.error("❌ Failed to load screenshot for visualization")
                return False

            # Initialize debug visualization
            if not self.debugger.load_screenshot("screen.png"):
                logging.error("❌ Failed to initialize debug visualization")
                return False

            # Focus on the bottom part of the screen only
            bottom_region_y = screenshot.shape[0] - 150  # Bottom 150 pixels where troops usually are
            logging.info(f"Drawing deployment region at y={bottom_region_y}")
            self.debugger.draw_deployment_region(
                bottom_region_y,
                screenshot.shape[1],
                screenshot.shape[0]
            )

            # Loop through each element with a more efficient approach
            logging.info("Starting troop detection...")
            for element_name, (image_file, count) in elements_to_detect.items():
                image_path = os.path.join(self.image_folder, image_file)
                logging.info(f"Checking for {element_name} using {image_file}...")

                # Skip if the reference image doesn't exist
                if not os.path.exists(image_path):
                    logging.warning(f"⚠️ Reference image not found: {image_file}")
                    continue

                # Look for the element in the screenshot
                pos, confidence = self.image.find_image("screen.png", image_path)
                logging.info(f"Detection result for {element_name}: pos={pos}, confidence={confidence:.2f}")

                if pos and confidence > 0.65:  # Reduced threshold for better detection
                    # Mark as detected
                    self.deployment_locations[element_name] = {
                        "position": pos,
                        "count": count,
                        "confidence": confidence
                    }
                    detected_count += 1
                    
                    # Count heroes separately
                    if element_name.startswith("hero"):
                        hero_count += 1

                    # Add to debug visualization
                    template = cv2.imread(image_path)
                    if template is not None:
                        h, w = template.shape[:2]
                        self.debugger.draw_troop_detection(pos, (w, h), element_name, confidence, count)
                        logging.info(f"✅ Detected {element_name} at {pos} with confidence {confidence:.2f} (size: {w}x{h})")
                    else:
                        logging.warning(f"⚠️ Could not load template image for {element_name}")

            # Check if we have enough heroes
            if hero_count < 4:  # Need at least 4 heroes
                logging.warning(f"⚠️ Only {hero_count}/4 heroes detected - aborting attack")
                return False

            # Save the debug visualization
            logging.info("Saving debug visualization...")
            self.debugger.save_visualization("troop_detection.png")

            logging.info(f"✅ Prepared {detected_count} deployment elements ({hero_count} heroes)")
            for name, data in self.deployment_locations.items():
                logging.info(f"  • {name}: position={data['position']}, count={data['count']}, confidence={data['confidence']:.2f}")

            return True

        except Exception as e:
            logging.error(f"❌ Error during deployment preparation: {e}")
            return False

    def use_default_deployment(self):
        """Helper method to set default deployment positions"""
        self.deployment_locations = {
            "super_minion": {"position": (100, 600), "count": 25},
            "ice_spell": {"position": (240, 600), "count": 1},
            "rage_spell":{"position": (200, 600), "count": 5},
            "hero_5": {"position": (500, 600), "count": 1},
            "hero_3": {"position": (300, 600), "count": 1},
            "hero_4": {"position": (350, 600), "count": 1},
            "hero_2": {"position": (400, 600), "count": 1},
            "hero_1": {"position": (450, 600), "count": 1},
        }
        logging.info("Using default deployment positions")

    def deploy_units(self, element_name, target_locations):
        """
        Deploy a specific element (troop, spell, hero, or ability) to multiple target locations on the battlefield.

        Args:
            element_name: The name of the element to deploy.
            target_locations: A list of tuples [(x1, y1), (x2, y2), ...] representing the coordinates to deploy each unit.
        """
        if element_name not in self.deployment_locations:
            logging.error(f"❌ Element {element_name} not prepared for deployment")
            return False

        element_data = self.deployment_locations[element_name]
        element_pos = element_data["position"]
        unit_count = element_data["count"]
        confidence = element_data["confidence"]

        # Use only the required number of locations
        target_count = min(unit_count, len(target_locations))

        logging.info(f"Deploying {target_count} units of {element_name} (confidence: {confidence:.2f})")

        # Click the element with retries
        max_retries = 3
        click_success = False
        
        for attempt in range(max_retries):
            logging.info(f"Attempt {attempt + 1}/{max_retries}: Clicking {element_name} at position {element_pos}")
            
            # Add a small random delay before clicking
            time.sleep(random.uniform(0.1, 0.3))
            
            # Try to click the element
            click_success = self.adb.humanlike_click(*element_pos)
            
            if click_success:
                logging.info(f"✅ Successfully clicked {element_name}")
                break
            else:
                if attempt < max_retries - 1:
                    logging.warning(f"⚠️ Failed to click {element_name}, retrying...")
                    time.sleep(0.5)  # Wait before retry
                else:
                    logging.error(f"❌ Failed to click {element_name} after {max_retries} attempts")
                    return False

        # Wait for troop selection to register
        

        # Verify the element is selected by taking a screenshot
        if not self.adb.take_screenshot("screen.png"):
            logging.error("❌ Failed to take screenshot for deployment verification")
            return False

        # Deploy troops to predefined locations
        successful_deployments = 0
        for i in range(target_count):
            target_x, target_y = target_locations[i]
            logging.info(f"Deploying unit {i+1}/{target_count} to ({target_x}, {target_y})")
            
            # Add a small random delay before each deployment
            time.sleep(random.uniform(0.1, 0.3))
            
            # Try to deploy the unit
            if self.adb.humanlike_click(target_x, target_y):
                successful_deployments += 1
                logging.info(f"✅ Successfully deployed unit {i+1}")
            else:
                logging.warning(f"⚠️ Failed to deploy unit {i+1}")
                
            # Random delay between deployments for human-like behavior
            time.sleep(random.uniform(0.01, 0.1))

        # Check if we had enough successful deployments
        if successful_deployments < target_count * 0.5:  # At least 50% of deployments should succeed
            logging.error(f"❌ Too many failed deployments ({successful_deployments}/{target_count})")
            return False

        logging.info(f"✅ Successfully deployed {successful_deployments}/{target_count} units")
        return True

    def deploy_all(self):
        """
        Deploy all troops, spells, and heroes to their respective locations.
        Uses a more efficient deployment sequence with randomized and shuffled locations.
        """
        # Define optimized troop locations (no duplicates)
        troop_locations = [
            (173, 380), (198, 395), (220, 413), (252, 438), (293, 464),
            (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
            (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
            (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
            (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
        ]

        spell_locations = [(588, 272), (494, 395), (583, 205), (636, 395), (632, 542)]
        ice_spell_locations = [(789, 345)]

        # More strategic hero deployment positions
        hero_locations = [(149, 320), (194, 379), (214, 261), (157, 325)]

        # Shuffle the deployment locations for troops and heroes
        random.shuffle(troop_locations)
        random.shuffle(hero_locations)
        random.shuffle(spell_locations)

        # Check for all 5 heroes but only deploy 4
        all_heroes = ["hero_1", "hero_2", "hero_3", "hero_4", "hero_5"]
        available_heroes = []
        
        # First check which heroes are present
        for hero_name in all_heroes:
            if hero_name in self.deployment_locations:
                available_heroes.append(hero_name)
        
        # If we have more than 4 heroes, randomly select 4 to deploy
        if len(available_heroes) > 4:
            logging.info(f"Found {len(available_heroes)} heroes, selecting 4 to deploy")
            random.shuffle(available_heroes)
            available_heroes = available_heroes[:4]
        
        logging.info(f"Deploying heroes: {', '.join(available_heroes)}")

        # Deploy troops
        logging.info("Deploying troops...")
        if not self.deploy_units("super_minion", troop_locations):
            logging.error("❌ Failed to deploy troops - aborting attack")
            return False

        # Deploy available heroes
        logging.info(f"Deploying {len(available_heroes)} heroes...")
        for i, hero_name in enumerate(available_heroes):
            if i < len(hero_locations):  # Ensure we have a location for this hero
                if not self.deploy_units(hero_name, [hero_locations[i]]):
                    logging.error(f"❌ Failed to deploy {hero_name} - continuing with other heroes")
                    continue
                time.sleep(0.1)  
        # Deploy spells
        time.sleep(1)  # Reduced from 2 seconds
        logging.info("Deploying spells...")
        if not self.deploy_units("rage_spell", spell_locations):
            logging.error("❌ Failed to deploy rage spells - continuing with other spells")
            
        time.sleep(1.5) 
        logging.info("Deploying ice spell...")
        if not self.deploy_units("ice_spell", ice_spell_locations):
            logging.error("❌ Failed to deploy ice spell - continuing with abilities")

        # Activate hero abilities with reduced delay
        self.activate_hero_abilities(available_heroes, ability_delay=2)  
        return True

    def activate_hero_abilities(self, hero_names, ability_delay=3):
        """
        Activate hero abilities after a delay by clicking their card positions again.

        Args:
            hero_names: A list of hero names whose abilities to activate.
            ability_delay: Delay in seconds before using hero abilities.
        """
        # Wait before using abilities - reduced from 5 seconds
        logging.info(f"Waiting {ability_delay} seconds before using hero abilities")
        time.sleep(ability_delay)

        # Use hero abilities
        for hero_name in hero_names:
            if hero_name not in self.deployment_locations:
                continue  # Skip missing heroes without error message

            hero_data = self.deployment_locations[hero_name]
            hero_pos = hero_data["position"]

            logging.info(f"Using ability for hero {hero_name} at position {hero_pos}")
            # Pass x, y separately to avoid tuple error
            self.adb.humanlike_click(hero_pos[0], hero_pos[1])
            time.sleep(0.3)  # Reduced from 0.5 seconds

        return True

    def execute_attack_cycle(self, max_searches=30000):
        """
        Execute a full attack cycle: search for a base, execute the attack, and return home.
        
        Args:
            max_searches: Maximum number of searches to perform for a suitable base.
        
        Returns:
            bool: True if the attack cycle was completed successfully, False otherwise.
        """
        logging.info("\n" + "=" * 50)
        logging.info("STARTING ATTACK CYCLE")
        logging.info("=" * 50)

        # Search for a base
        if not self.search_sequence.search_for_base(max_searches):
            logging.warning("⚠️ No suitable base found for attack.")
            return False
        # Execute the attack
        logging.info("Executing attack...")
        attack_success = self.execute_attack()

        if not attack_success:
            logging.warning("⚠️ Attack failed or encountered issues.")

        # Return to home screen
        if not self.navigate_to_home():
            logging.warning("⚠️ Failed to navigate back to home screen after attack.")

        return True
