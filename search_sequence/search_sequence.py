import os
import time
import logging
import cv2
import numpy as np
import pytesseract
import random

from utils.image_utils import ImageUtils
from utils.adb_utils import ADBUtils
from utils.debug_utils import DebugVisualizer
from utils.main_utils import click_button, wait_for_ui_stabilization

class SearchSequence:
    def __init__(self, gold_threshold=1000000, elixir_threshold=1000000, dark_threshold=5000, debug_mode=True):
        self.adb = ADBUtils()
        self.image = ImageUtils(debug_mode=debug_mode)
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")
        self.gold_threshold = gold_threshold
        self.elixir_threshold = elixir_threshold
        self.dark_threshold = dark_threshold

        # Wider bounding boxes for resource detection (x1, y1, x2, y2)
        self.gold_bbox = (95, 95, 220, 120)  # Top left region - Gold
        self.elixir_bbox = (95, 135, 220, 160)  # Top center region - Elixir
        self.dark_bbox = (95, 175, 200, 200)  # Top right region - Dark Elixir

        self.debugger = DebugVisualizer(debug_mode=debug_mode)

        logging.info("\n" + "="*50)
        logging.info("SEARCH SEQUENCE INITIALIZED")
        logging.info(f"Resource Thresholds - Gold: {gold_threshold:,}, Elixir: {elixir_threshold:,}, Dark: {dark_threshold:,}")
        logging.info("="*50)

    def click_initial_buttons(self):
        """Click 'attack_button.png' first, then attempt to click 'find_match.png' if available."""

        # First, always click "attack_button.png"
        if click_button(self.image, self.adb, self.image_folder, "attack_button.png"):
            # Verify attack menu
            if self.verify_attack_menu():
                ...
            else:
                logging.warning("⚠️ Attack menu not detected after click, retrying...")
                wait_for_ui_stabilization(3)

        # Now, check for "find_match.png" and click it if found
        if click_button(self.image, self.adb, self.image_folder, "find_match.png"):
            logging.info("⏳ Waiting for resources to load...")
            wait_for_ui_stabilization(0.5)

        # Short delay to ensure UI stability
        logging.info("⏳ Waiting for resources to appear...")
        time.sleep(4)

    def verify_attack_menu(self):
        """Verify we're in the attack menu by looking for the find_match button"""
        return self.image.detect_image(self.adb, self.image_folder, "find_match.png", confidence_threshold=0.6)

    def preprocess_image_for_ocr(self, img):
        """Preprocess image for OCR to improve text recognition"""
        # Cache the preprocessed image
        if not hasattr(self, '_preprocessed_cache'):
            self._preprocessed_cache = {}
        
        # Convert image to string for caching
        img_str = str(img.tobytes())
        if img_str in self._preprocessed_cache:
            return self._preprocessed_cache[img_str]
            
        # Apply preprocessing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        inverted = cv2.bitwise_not(blurred)
        
        # Store in cache
        self._preprocessed_cache[img_str] = inverted
        return inverted

    def try_multiple_ocr(self, img):
        """Enhanced OCR with optimized processing"""
        # Use the most effective PSM mode first
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        
        try:
            # Try the most reliable configuration first without language specification
            result = pytesseract.image_to_string(img, config=custom_config)
            if any(c.isdigit() for c in result):
                return result.strip()
                
            # If first attempt fails, try alternative PSM modes
            for psm in [8, 13]:
                result = pytesseract.image_to_string(
                    img,
                    config=f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789'
                )
                if any(c.isdigit() for c in result):
                    return result.strip()
                    
        except Exception as e:
            logging.warning(f"OCR error: {str(e)}")
            # Try one last time with minimal configuration
            try:
                result = pytesseract.image_to_string(img, config='--oem 3 --psm 7')
                if any(c.isdigit() for c in result):
                    return result.strip()
            except:
                pass
            
        return ""

    def extract_number(self, text):
        """Improved validation with game-specific checks"""
        clean = ''.join(c for c in text if c.isdigit())
        if not clean:
            return 0

        num = int(clean)

        if num < 1000:  # Minimum reasonable resources
            return 0
        if num > 4000000:  # Maximum possible in CoC
            return 0

        return num

    def extract_resource_amounts(self) -> tuple[int, int, int]:
        """Enhanced extraction with optimized processing"""
        logging.info("Taking screenshot for resource detection")
        
        if not self.adb.take_screenshot("screen.png"):
            return 0, 0, 0

        self.debugger.load_screenshot("screen.png")
        screenshot = cv2.imread("screen.png")
        if screenshot is None:
            return 0, 0, 0

        # Extract regions once
        regions = {
            'gold': screenshot[self.gold_bbox[1]:self.gold_bbox[3], self.gold_bbox[0]:self.gold_bbox[2]],
            'elixir': screenshot[self.elixir_bbox[1]:self.elixir_bbox[3], self.elixir_bbox[0]:self.elixir_bbox[2]],
            'dark': screenshot[self.dark_bbox[1]:self.dark_bbox[3], self.dark_bbox[0]:self.dark_bbox[2]]
        }

        # Validate regions
        for name, region in regions.items():
            if region.shape[0] < 20 or region.shape[1] < 50:
                logging.error(f"Invalid {name} region size: {region.shape}")
                return 0, 0, 0

        # Process all regions at once
        results = {}
        for name, region in regions.items():
            preprocessed = self.preprocess_image_for_ocr(region)
            text = self.try_multiple_ocr(preprocessed)
            results[name] = self.extract_number(text)

        gold, elixir, dark = results['gold'], results['elixir'], results['dark']

        # Debug visualization
        text_offset_x = 210
        text_offset_y = 30

        self.debugger.draw_resource_info(self.gold_bbox, gold, self.gold_threshold, "Gold", text_offset_x, text_offset_y)
        self.debugger.draw_resource_info(self.elixir_bbox, elixir, self.elixir_threshold, "Elixir", text_offset_x, text_offset_y)
        self.debugger.draw_resource_info(self.dark_bbox, dark, self.dark_threshold, "Dark", text_offset_x, text_offset_y)

        self.debugger.draw_thresholds(text_offset_x, self.gold_threshold, self.elixir_threshold, self.dark_threshold)

        resources_met = sum([
            1 if gold >= self.gold_threshold else 0,
            1 if elixir >= self.elixir_threshold else 0,
            1 if dark >= self.dark_threshold else 0
        ])
        meets = resources_met >= 2
        decision = "ATTACK" if meets else "SKIP"

        self.debugger.draw_decision(text_offset_x, resources_met, meets, decision)
        self.debugger.save_visualization("result.png")

        logging.info(f"Resources - Gold: {gold}, Elixir: {elixir}, Dark: {dark} | Decision: {decision}")
        logging.info(f"Resource detection results:")
        logging.info(f"  Gold detected:   {gold:,} {'✓' if gold >= self.gold_threshold else '✗'}")
        logging.info(f"  Elixir detected: {elixir:,} {'✓' if elixir >= self.elixir_threshold else '✗'}")
        logging.info(f"  Dark detected:   {dark:,} {'✓' if dark >= self.dark_threshold else '✗'}")

        return gold, elixir, dark

    def click_skip_button(self):
        """Click the next/skip button to move to the next base"""
        logging.info("Attempting to click next button...")
        
        max_retries = 3
        for attempt in range(max_retries):
            # Try with normal confidence first
            if self.image.find_and_click_image(self.adb, self.image_folder, "next_button.png", log_prefix="[SKIP] "):
                logging.info("Next button clicked, waiting for new base to load...")
                return True
                
            # If failed, try with lower confidence threshold
            if attempt < max_retries - 1:
                logging.info(f"Retry {attempt + 1}/{max_retries} with lower confidence...")
                if self.image.find_and_click_image(self.adb, self.image_folder, "next_button.png", 
                                                 confidence_threshold=0.4, log_prefix="[SKIP] "):
                    logging.info("Next button clicked with lower confidence, waiting for new base to load...")
                    return True
                    
            time.sleep(0.5)  # Short delay between attempts
            
        logging.warning("Could not find next/skip button after multiple attempts - search may be interrupted")
        return False

    def meets_threshold(self, gold: int, elixir: int, dark: int) -> bool:
        """Check if at least TWO resources meet or exceed the defined thresholds"""
        resources_met = 0

        if gold >= self.gold_threshold:
            resources_met += 1

        if elixir >= self.elixir_threshold:
            resources_met += 1

        if dark >= self.dark_threshold:
            resources_met += 1

        return resources_met >= 2

    def reset_search_state(self):
        """Reset the search state to prepare for a new search sequence"""
        logging.info("Resetting search state for a new search cycle")
        return True

    def search_for_base(self, max_searches=30000):
        """Search for a base with resources meeting the thresholds"""
        logging.info("\n" + "="*50)
        logging.info(f"STARTING BASE SEARCH (max attempts: {max_searches})")
        logging.info(f"ATTACK CRITERIA: At least 2 of 3 resources must meet thresholds")
        logging.info("="*50)

        self.reset_search_state()

        try:
            self.click_initial_buttons()
        except Exception as e:
            logging.error(f"❌ Error clicking initial buttons: {e}")
            return False

        for attempt in range(max_searches):
            logging.info("\n" + "-"*40)
            logging.info(f"SEARCH ATTEMPT {attempt + 1}/{max_searches}")
            logging.info("-"*40)

            try:
                gold, elixir, dark = self.extract_resource_amounts()

                gold_indicator = "✓" if gold >= self.gold_threshold else "✗"
                elixir_indicator = "✓" if elixir >= self.elixir_threshold else "✗"
                dark_indicator = "✓" if dark >= self.dark_threshold else "✗"

                resources_met = sum([
                    1 if gold >= self.gold_threshold else 0,
                    1 if elixir >= self.elixir_threshold else 0,
                    1 if dark >= self.dark_threshold else 0
                ])

                if self.meets_threshold(gold, elixir, dark):
                    logging.info("\n" + "*"*50)
                    logging.info(f"BASE FOUND - {resources_met}/3 THRESHOLDS MET - ATTACKING!")
                    logging.info("*"*50 + "\n")
                    return True

                logging.info(f"Base does not meet requirements ({resources_met}/3 thresholds) - SKIPPING")
                self.click_skip_button()

            except Exception as e:
                logging.error(f"❌ Error during search attempt {attempt + 1}: {e}")
                self.click_skip_button()
                time.sleep(1)

        logging.info("\n" + "="*50)
        logging.info(f"SEARCH COMPLETE - Max attempts ({max_searches}) reached")
        logging.info("="*50)
        return False

    def calibrate_detection_areas(self):
        """Take a screenshot and draw test boxes to help calibrate resource detection areas"""
        logging.info("Calibrating resource detection areas")

        if not self.adb.take_screenshot("calibration.png"):
            logging.error("Failed to take screenshot for calibration")
            return

        self.debugger.load_screenshot("calibration.png")

        boxes = [
            (self.gold_bbox, "Gold", (0, 200, 255)),
            (self.elixir_bbox, "Elixir", (180, 0, 180)),
            (self.dark_bbox, "Dark", (0, 0, 0))
        ]

        for box, label, color in boxes:
            x1, y1, x2, y2 = box
            width = x2 - x1
            height = y2 - y1

            self.debugger.draw_detection(
                (x1, y1),
                (width, height),
                f"{label}: ({x1}, {y1}, {x2}, {y2})",
                color=color
            )

        self.calibrate_button_detection()

        self.debugger.save_visualization("calibration_boxes.png")
        logging.info("Saved calibration image to calibration_boxes.png")

    def calibrate_button_detection(self):
        """Find and highlight buttons to calibrate button detection"""
        logging.info("Calibrating button detection")

        buttons = ["attack_button.png", "find_match.png", "next_button.png"]

        for button in buttons:
            button_path = os.path.join(self.image_folder, button)
            if not os.path.exists(button_path):
                logging.warning(f"Button template not found: {button_path}")
                continue

            pos, confidence = self.image.find_image("calibration.png", button_path)

            if pos:
                template = cv2.imread(button_path)
                if template is None:
                    continue

                h, w = template.shape[:2]

                self.debugger.draw_button_detection(pos, (w, h), button, confidence)
            else:
                logging.warning(f"Button not detected: {button}")
