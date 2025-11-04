from typing import Callable, Dict, List, Optional, Tuple
import random
import time
import easyocr


class WallUpgradeManager:
    """Coordinates the wall upgrade sequence using OCR and UI hooks.

    This class is UI-framework agnostic. All device interactions are provided
    via the hooks dictionary passed to public methods.

    Required hooks:
      - 'device_id': str
      - 'take_screenshot': Callable[[], None]
      - 'detect_and_tap_button': Callable[[str], bool]
      - 'human_tap': Callable[[int, int, int], None]
      - 'detect_button': Callable[[str], Optional[Tuple[int, int]]]
    """

    def __init__(
        self,
        builder_menu_button_folder: str,
        screenshot_name: str,
        random_offset: int,
        ocr_region: Optional[Tuple[int, int, int, int]] = None,
        keywords: Optional[List[str]] = None,
        gpu: bool = False,
        target_text_region: Optional[Tuple[int, int, int, int]] = None,
        okay_button_folder: Optional[str] = None,
        gem_icon_folder: Optional[str] = None,
        close_button_folder: Optional[str] = None,
    ) -> None:
        self.builder_menu_button_folder = builder_menu_button_folder
        self.screenshot_name = screenshot_name
        self.random_offset = random_offset
        self.next_wall_upgrade_at = None
        self._ocr_reader = easyocr.Reader(['en'], gpu=gpu)
        self.ocr_region = ocr_region
        self.keywords = [k.lower() for k in (keywords or ["wall", "walls"])]
        self.target_text_region = target_text_region
        self.okay_button_folder = okay_button_folder
        self.gem_icon_folder = gem_icon_folder
        self.close_button_folder = close_button_folder

    def schedule_next_wall_upgrade(self, current_attack_count: int) -> None:
        """Set the next wall upgrade attempt 2–3 attacks ahead."""
        self.next_wall_upgrade_at = current_attack_count + random.randint(2, 3)
        print(f"🧱 Next wall upgrade scheduled at attack #{self.next_wall_upgrade_at}")

    def _find_text_center_on_screen(
        self,
        needle_text: str,
        hooks: Dict[str, Callable],
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Optional[Tuple[int, int]]:
        import cv2
        img = cv2.imread(self.screenshot_name)
        if img is None:
            return None
        if region is not None:
            x1, y1, x2, y2 = region
            img = img[y1:y2, x1:x2]
        results = self._ocr_reader.readtext(img)
        needle_lower = needle_text.lower()
        for (bbox, text, _conf) in results:
            if text and needle_lower in text.lower():
                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]
                cx = int(sum(xs) / 4)
                cy = int(sum(ys) / 4)
                if region is not None:
                    cx += region[0]
                    cy += region[1]
                return (cx, cy)
        return None

    def _human_swipe(self, hooks: Dict[str, Callable], sx: int, sy: int, ex: int, ey: int) -> None:
        import subprocess
        device_id = hooks['device_id']
        duration = random.randint(200, 400)
        cmd = [
            "adb", "-s", device_id, "shell", "input", "swipe",
            str(sx + random.randint(-10, 10)),
            str(sy + random.randint(-10, 10)),
            str(ex + random.randint(-10, 10)),
            str(ey + random.randint(-10, 10)),
            str(duration)
        ]
        try:
            subprocess.run(cmd, check=True)
        except Exception:
            pass

    def open_builder_menu_and_select_wall(self, hooks: Dict[str, Callable]) -> bool:
        hooks['take_screenshot']()
        if not hooks['detect_and_tap_button'](self.builder_menu_button_folder):
            print("⚠️ Builder menu button not found:", self.builder_menu_button_folder)
            return False
        time.sleep(random.uniform(0.7, 1.1))

        for _ in range(10):
            time.sleep(random.uniform(0.4, 0.8))
            hooks['take_screenshot']()
            for kw in self.keywords:
                center = self._find_text_center_on_screen(kw, hooks, region=self.ocr_region)
                if center:
                    print(f"🔎 Found '{kw}' at {center}, tapping...")
                    hooks['human_tap'](center[0], center[1], self.random_offset)
                    time.sleep(random.uniform(0.5, 0.9))
                    return True
            self._human_swipe(hooks, 830, 470, 830, 270)
        print("⚠️ 'Wall' not found in builder menu after scrolling.")
        return False

    def _attempt_single_upgrade(self, hooks: Dict[str, Callable]) -> bool:
        time.sleep(random.uniform(0.4, 0.8))
        upgrade_found = False
        for _ in range(3):
            hooks['take_screenshot']()
            center = self._find_text_center_on_screen("@pgrade", hooks, region=self.target_text_region)
            if center:
                print(f"✅ Found Upgrade at {center}; tapping")
                hooks['human_tap'](center[0], center[1], self.random_offset)
                upgrade_found = True
                time.sleep(random.uniform(0.3, 0.6))
                break
            time.sleep(0.2)

        confirm_found = False
        for _ in range(3):
            hooks['take_screenshot']()
            center = (
                self._find_text_center_on_screen("Coufian", hooks, region=self.target_text_region)
                or self._find_text_center_on_screen("Confian", hooks, region=self.target_text_region)
            )
            if center:
                print(f"✅ Found Confirm at {center}; tapping")
                hooks['human_tap'](center[0], center[1], self.random_offset)
                confirm_found = True
                time.sleep(random.uniform(0.3, 0.6))
                break
            time.sleep(1)

        if self.okay_button_folder:
            hooks['take_screenshot']()
            gem_coords = hooks['detect_button'](self.okay_button_folder)
            if gem_coords:
                hooks['human_tap'](gem_coords[0], gem_coords[1], self.random_offset)
                time.sleep(random.uniform(0.25, 0.5))

        if self.gem_icon_folder:
            hooks['take_screenshot']()
            gem_coords = hooks['detect_button'](self.gem_icon_folder)
            if gem_coords:
                print("💎 Gem icon detected; closing dialog (2 taps)")
                for _ in range(2):
                    hooks['take_screenshot']()
                    close_coords = hooks['detect_button'](self.close_button_folder)
                    if close_coords:
                        hooks['human_tap'](close_coords[0], close_coords[1], self.random_offset)
                        time.sleep(random.uniform(0.25, 0.5))
                self.last_gem_abort = True
                return False

        return upgrade_found or confirm_found

    def perform_wall_upgrade_sequence(self, hooks: Dict[str, Callable]) -> bool:
        """Select wall and attempt two upgrade buttons (gold, elixir) in sequence."""
        self.last_gem_abort = False
        if not self.open_builder_menu_and_select_wall(hooks):
            return False
        successes = 0
        for _ in range(2):
            if self.last_gem_abort:
                break
            if self._attempt_single_upgrade(hooks):
                successes += 1
            time.sleep(random.uniform(0.4, 0.7))
        return successes > 0

    def maybe_upgrade_walls(self, current_attack_count: int, hooks: Dict[str, Callable]) -> None:
        if self.next_wall_upgrade_at is None:
            self.schedule_next_wall_upgrade(current_attack_count)
            return
        if current_attack_count < self.next_wall_upgrade_at:
            return

        print(f"\n===== WALL UPGRADE WINDOW (attack #{current_attack_count}) =====")
        hooks['take_screenshot']()
        hooks['detect_and_tap_button']("ui_main_base/okay_button")
        time.sleep(random.uniform(0.4, 0.8))

        ok = self.perform_wall_upgrade_sequence(hooks)
        if ok:
            print("✅ Wall upgrade routine completed with at least one success.")
        else:
            print("ℹ️ No wall upgrades applied this time.")
        self.schedule_next_wall_upgrade(current_attack_count)


