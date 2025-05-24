## `utils/image_utils.py`

import cv2
import logging
import os
from utils.debug_utils import DebugVisualizer

class ImageUtils:
    """Simple image utility for template matching and annotation."""
    def __init__(self):
        self.debugger = DebugVisualizer()
        self._seen = set()

    def _log_once(self, msg: str):
        if msg not in self._seen:
            logging.info(msg)
            self._seen.add(msg)

    def find_image(self, screenshot: str, template: str) -> tuple[tuple[int,int]|None, float]:
        """Find template in screenshot. Returns (position, confidence)."""
        img = cv2.imread(screenshot)
        tpl = cv2.imread(template)
        if img is None or tpl is None:
            self._log_once("Image load failure")
            return None, 0.0
        res = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
        _, maxv, _, maxloc = cv2.minMaxLoc(res)
        return (maxloc, maxv*100) if maxv>0.8 else (None, maxv*100)

    def find_and_click_image(self, adb, folder: str, name: str, thr: float=0.7) -> bool:
        """Find and click image if confidence is above threshold."""
        path = os.path.join(folder, name)
        pos, pct = self.find_image("screen.png", path)
        conf = pct/100
        self._log_once(f"{name} confidence: {conf:.2f}")
        if pos and conf>=thr:
            h,w = cv2.imread(path).shape[:2]
            x,y = pos[0]+w//2, pos[1]+h//2
            adb.humanlike_click(x,y)
            return True
        return False

    def find_and_click_image_now(self, adb, folder: str, name: str, thr: float=0.7) -> bool:
        return self.find_and_click_image(adb, folder, name, thr)
