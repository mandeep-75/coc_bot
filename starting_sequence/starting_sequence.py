from utils.adb_utils import ADBUtils
from utils.image_utils import ImageUtils
import os
import time

class StartingSequence:
    def __init__(self, device_serial: str):
        self.adb = ADBUtils(serial=device_serial)
        self.image = ImageUtils()
        self.image_folder = os.path.join(os.path.dirname(__file__), "images")

    def go_home(self):
        self.adb.take_screenshot("screen.png")
        base_optimal_postion = self.image.find_image(self.adb, self.image_folder, "home_anchor.png")
        time.sleep(1)

    def collect_resources(self):
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "gold.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "elixir.png")
          self.image.find_and_click_image(self.adb, self.image_folder, "dark_elixir.png")
        time.sleep(1)

    def clear_popups(self):
        self.adb.take_screenshot("screen.png")
        self.image.find_and_click_image(self.adb, self.image_folder, "close.png")
        time.sleep(1)

    def run(self):
        self.go_home()
        self.clear_popups()
        self.collect_resources() 