import subprocess
import cv2
import glob
import os
import random
import time
import config

class DeviceController:
    def __init__(self, device_id=None):
        self.device_id = device_id
        if not self.device_id:
            self.device_id = self.select_device()

    def select_device(self):
        """Auto-selects a device or asks the user."""
        adb_command = ["adb", "devices"]
        try:
            result = subprocess.run(adb_command, capture_output=True, text=True, check=True)
            devices = [line.split('\t')[0] for line in result.stdout.strip().split('\n')[1:]
                       if line.strip() and '\tdevice' in line]
            if not devices:
                print("❌ No devices connected.")
                return None
            if len(devices) == 1:
                print(f"✅ One device detected: {devices[0]} (auto-selected)")
                return devices[0]
            
            print("📱 Connected devices:")
            for i, d in enumerate(devices):
                print(f"{i + 1}: {d}")
            # For automation safety, just pick the first one if multiple are present and no input mechanism
            # or we could try to prompt. For now, default to first.
            print(f"✅ Auto-selecting first device: {devices[0]}")
            return devices[0]
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to execute ADB command: {e}")
            return None

    def tap(self, x, y, offset=0):
        """Performs a human-like tap with random offset."""
        if not self.device_id:
            print("⚠️ No device connected.")
            return

        tx = x + random.randint(-offset, offset)
        ty = y + random.randint(-offset, offset)
        cmd = ["adb", "-s", self.device_id, "shell", "input", "tap", str(tx), str(ty)]
        try:
            subprocess.run(cmd, check=True)
            # print(f"Tapped at ({tx}, {ty})") 
        except subprocess.CalledProcessError as e:
            print(f"Failed to tap: {e}")

    def take_screenshot(self, local_path=config.SCREENSHOT_NAME):
        """Captures a screenshot from the device."""
        if not self.device_id:
            return
        try:
            cmd = f"adb -s {self.device_id} exec-out screencap -p > {local_path}"
            subprocess.run(cmd, shell=True, check=True)
            # print(f"Screenshot saved: {local_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to take screenshot: {e}")

    def detect_button(self, button_folder, screenshot_path=config.SCREENSHOT_NAME, threshold=0.8):
        """
        Detects a button/template on the screen.
        Returns (x, y) tuple if found, else None.
        """
        if not os.path.exists(screenshot_path):
            print(f"Screenshot not found: {screenshot_path}")
            return None

        screen = cv2.imread(screenshot_path)
        if screen is None:
            return None

        template_paths = glob.glob(os.path.join(button_folder, '*'))
        if not template_paths:
            print(f"No templates in {button_folder}")
            return None

        best_val = -1
        best_loc = None
        best_w, best_h = 0, 0

        for template_path in template_paths:
            template = cv2.imread(template_path)
            if template is None:
                continue
            
            try:
                res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            except cv2.error:
                continue

            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val and max_val >= threshold:
                best_val = max_val
                best_loc = max_loc
                best_w, best_h = template.shape[1], template.shape[0]

        if best_loc:
            x = best_loc[0] + best_w // 2
            y = best_loc[1] + best_h // 2
            print(f"✅ Found {os.path.basename(button_folder)} at ({x},{y}) conf={best_val*100:.1f}%")
            return x, y
        return None

    def detect_and_tap(self, button_folder, screenshot_path=config.SCREENSHOT_NAME, threshold=0.8, offset=config.RANDOM_OFFSET):
        """Detects a button and taps it immediately."""
        coords = self.detect_button(button_folder, screenshot_path, threshold)
        if coords:
            self.tap(coords[0], coords[1], offset)
            return True
        return False
