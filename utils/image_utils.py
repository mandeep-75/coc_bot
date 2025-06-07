import cv2
import numpy as np
import logging
import os
from utils.debug_utils import DebugVisualizer

class ImageUtils:
    def __init__(self, debug_mode: bool = True):
        self.debugger = DebugVisualizer(debug_mode=debug_mode)
        self.logged_messages = set()  # Set to track logged messages

    def log_once(self, message: str) -> None:
        """Log a message only once per instance."""
        if message not in self.logged_messages:
            logging.info(message)
            self.logged_messages.add(message)

    def find_image(self, screenshot_path: str, template_path: str) -> tuple[tuple[int, int] | None, float]:
        """
        Find a template image within a screenshot.
        Args:
            screenshot_path: Path to the screenshot image file.
            template_path: Path to the template image file.
        Returns:
            Tuple of ((x, y), match_percentage) if found, (None, 0.0) otherwise.
        """
        try:
            # Read the images
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)
            
            if screenshot is None or template is None:
                self.log_once("Failed to load images")
                return None, 0.0

            # Perform template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Create debug visualization
            self.debugger.load_screenshot(screenshot_path)
            match_threshold = 0.8
            matched = max_val > match_threshold
            match_percentage = max_val * 100
            
            # Draw detection box on result
            template_name = os.path.basename(template_path)
            confidence_text = f"{template_name} ({match_percentage:.1f}%)"
            
            if matched:
                self.debugger.draw_detection(max_loc, template.shape[:2], confidence_text, color=(0, 255, 0))
            else:
                self.debugger.draw_detection(max_loc, template.shape[:2], confidence_text, color=(0, 0, 255))
                
            # Save the visualization
            self.debugger.save_visualization("result.png")

            # If the match is good enough, return the position and match percentage
            if matched:  # Threshold for matching
                return max_loc, match_percentage
            return None, match_percentage

        except Exception as e:
            self.log_once(f"Error in image matching: {e}")
            return None, 0.0

    def _click_on_image(self, adb_utils, pos: tuple, image_path: str, image_name: str, center_click: bool, log_prefix: str = "") -> None:
        """Helper to click on an image at the detected position."""
        template = cv2.imread(image_path)
        if center_click and template is not None:
            h, w = template.shape[:2]
            center_x = pos[0] + w // 2
            center_y = pos[1] + h // 2
            self.log_once(f"{log_prefix}Clicking {image_name} at center position ({center_x}, {center_y})")
            adb_utils.humanlike_click(center_x, center_y)
        else:
            self.log_once(f"{log_prefix}Clicking {image_name} at detection position {pos}")
            adb_utils.humanlike_click(*pos)

    def find_and_click_image(self, adb_utils, image_folder: str, image_name: str, 
                             confidence_threshold: float = 0.7, center_click: bool = True, log_prefix: str = "") -> bool:
        """
        Find an image on screen and click on it if found. Optionally customize log prefix.
        Args:
            adb_utils: Instance of ADBUtils for screenshot and clicking
            image_folder: Path to folder containing template images
            image_name: Name of the image file to find
            confidence_threshold: Minimum match confidence (0-1.0)
            center_click: If True, click center of image; if False, click top-left
            log_prefix: Optional prefix for log messages
        Returns:
            bool: True if image was found and clicked, False otherwise
        """
        image_path = os.path.join(image_folder, image_name)
        pos, match_percentage = self.find_image("screen.png", image_path)
        confidence = match_percentage / 100
        self.log_once(f"{log_prefix}Match confidence for {image_name}: {confidence:.3f} (threshold: {confidence_threshold:.2f})")
        if pos and confidence >= confidence_threshold:
            self._click_on_image(adb_utils, pos, image_path, image_name, center_click, log_prefix)
            return True
        self.log_once(f"{log_prefix}Image {image_name} not matched with sufficient confidence")
        return False

    def detect_image(self, adb_utils, image_folder: str, image_name: str, confidence_threshold=0.7) -> bool:
        """
        Just detect an image on screen without clicking.
        
        Args:
            adb_utils: Instance of ADBUtils for screenshot
            image_folder: Path to folder containing template images
            image_name: Name of the image file to find
            confidence_threshold: Minimum match confidence (0-1.0)
            
        Returns:
            bool: True if image was found, False otherwise
        """
        if not adb_utils.take_screenshot("screen.png"):
            return False
            
        image_path = os.path.join(image_folder, image_name)
        pos, match_percentage = self.find_image("screen.png", image_path)
        
        return pos is not None and match_percentage/100 >= confidence_threshold
