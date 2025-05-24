from utils.adb_utils import ADBUtils
from utils.image_utils import ImageUtils
import os
import time

class AttackSequence:
    def __init__(self, device_serial: str):
        self.adb = ADBUtils(serial=device_serial)
        self.image = ImageUtils()
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")

    def prepare_attack(self):
        """Prepare for attack (e.g., open attack menu)."""
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "attack_menu.png")
        time.sleep(1)

    def deploy_troops(self):
        """Deploy troops at strategic locations."""
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "super_minion.png")
        # Example: deploy at (300, 600)
        self.adb.humanlike_click(300, 600)
        time.sleep(1)

    def use_spells(self):
        """Use spells at the right time/position."""
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "spell_rage.png")
        self.adb.humanlike_click(400, 400)
        time.sleep(1)

    def finish_attack(self):
        """End the attack and return home."""
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "return_home.png")
        time.sleep(1)

    def run(self):
        self.prepare_attack()
        self.deploy_troops()
        self.use_spells()
        self.finish_attack() 