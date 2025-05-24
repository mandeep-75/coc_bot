from utils.adb_utils import ADBUtils
from utils.image_utils import ImageUtils
import os
import time

class SearchSequence:
    def __init__(self, device_serial: str):
        self.adb = ADBUtils(serial=device=device_serial)
        self.image = ImageUtils()
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")

    def open_attack_menu(self):
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "attack_menu.png")
        time.sleep(1)

    def find_match(self):
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "find_match_button.png")
        time.sleep(2)

    def evaluate_base(self):
        # Dummy logic: always accept the first base
        return True

    def skip_base(self):
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "skip_base_button.png")
        time.sleep(1)

    def run(self):
        self.open_attack_menu()
        while True:
            self.find_match()
            if self.evaluate_base():
                break
            self.skip_base() 