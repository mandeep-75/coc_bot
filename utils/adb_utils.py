import subprocess
import logging
import time
import random

class ADBUtils:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def execute_adb(self, command: str, shell=True) -> bool:
        """Execute an ADB command with retries and error handling."""
        for attempt in range(self.max_retries):
            try:
                if shell:
                    cmd = f"adb shell {command}"
                else:
                    cmd = f"adb {command}"
                    
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
                return True
            except subprocess.CalledProcessError as e:
                logging.error(f"ADB command failed (attempt {attempt + 1}): {e.stderr.strip()}")
                time.sleep(1)
        return False

    def take_screenshot(self, filename: str) -> bool:
        """Capture a screenshot and pull it to the local machine."""
        try:
            # Take screenshot on device
            if not self.execute_adb(f"screencap -p /sdcard/{filename}"):
                return False
                
            # Pull file from device to local machine
            if not self.execute_adb(f"pull /sdcard/{filename} .", shell=False):
                return False
                
            # Clean up file on device
            if not self.execute_adb(f"rm /sdcard/{filename}"):
                logging.warning("Failed to clean up screenshot on device")
                
            return True
        except Exception as e:
            logging.error(f"Screenshot failed: {e}")
            return False

    def humanlike_click(self, x: int, y: int):
        """Simulate a human-like click with randomness."""
        # If x, y is a tuple, unpack it
        if isinstance(x, tuple):
            x, y = x
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)
        self.execute_adb(f"input tap {x} {y}")
        time.sleep(random.uniform(0.2, 0.5))