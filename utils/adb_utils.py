## `utils/adb_utils.py`

import subprocess
import logging
import time
import random

class ADBUtils:
    """Simple ADB utility for device interaction. Add your own anti-detection logic as needed."""
    def __init__(self, serial: str = None, max_retries: int = 3):
        self.serial = serial
        self.max_retries = max_retries

    def _build_cmd(self, cmd: str, shell: bool = True) -> str:
        prefix = f"adb -s {self.serial} shell" if self.serial else "adb shell"
        return f"{prefix} {cmd}" if shell else f"adb {cmd}"

    def execute_adb(self, command: str, shell: bool = True) -> bool:
        for i in range(self.max_retries):
            try:
                full = self._build_cmd(command, shell)
                subprocess.run(full, shell=True, check=True, capture_output=True)
                return True
            except subprocess.CalledProcessError as e:
                logging.error(f"ADB failed (try {i+1}): {e.stderr.strip()}")
                time.sleep(1)
        return False

    def take_screenshot(self, filename: str) -> bool:
        """Take a screenshot from the device and pull it locally."""
        if not self.execute_adb(f"screencap -p /sdcard/{filename}"):
            return False
        if not self.execute_adb(f"pull /sdcard/{filename} .", shell=False):
            return False
        self.execute_adb(f"rm /sdcard/{filename}")
        return True

    def get_screen_dimensions(self) -> tuple[int, int]:
        out = subprocess.check_output(
            self._build_cmd("wm size", shell=True), shell=True, text=True
        )
        # e.g. "Physical size: 1080x1920"
        parts = out.strip().split()[-1].split('x')
        return int(parts[0]), int(parts[1])

    def humanlike_click(self, x: int, y: int):
        """Simulate a human-like tap with randomization."""
        rx = x + random.randint(-5, 5)
        ry = y + random.randint(-5, 5)
        self._random_delay()
        self.execute_adb(f"input tap {rx} {ry}")
        self._random_delay()

    def _random_delay(self):
        time.sleep(random.uniform(0.15, 0.6))

    def anti_detection_stub(self):
        """Add your own anti-detection logic here (e.g., random pauses, UI checks, etc)."""
        pass
