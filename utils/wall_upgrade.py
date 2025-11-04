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
        import cv2
        time.sleep(random.uniform(0.4, 0.8))

        # Collect all candidate Upgrade buttons by OCR (e.g., matches "@pgrade")
        hooks['take_screenshot']()
        img = cv2.imread(self.screenshot_name)
        if img is None:
            return False
        region = self.target_text_region
        if region is not None:
            x1, y1, x2, y2 = region
            crop = img[y1:y2, x1:x2]
        else:
            crop = img

        results = self._ocr_reader.readtext(crop)
        candidates: List[Tuple[int, int]] = []
        for (bbox, text, _conf) in results:
            if text and "@pgrade" in text.lower():
                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]
                cx = int(sum(xs) / 4)
                cy = int(sum(ys) / 4)
                if region is not None:
                    cx += region[0]
                    cy += region[1]
                candidates.append((cx, cy))

        # Consider only the last two upgrade buttons per selection (tap from the end)
        candidates = candidates[-2:]

        # Try each candidate upgrade button until one does NOT trigger a gem dialog
        ordered = list(reversed(candidates))  # start from the last, then second-last
        for idx, (ux, uy) in enumerate(ordered):
            print(f"✅ Found Upgrade[{idx+1}/{len(ordered)}] at ({ux}, {uy}); tapping")
            hooks['human_tap'](ux, uy, self.random_offset)
            time.sleep(random.uniform(0.3, 0.6))

            # Try to find and tap confirm
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

            # Tap any OK dialog if present (not the gem icon)
            if self.okay_button_folder:
                hooks['take_screenshot']()
                ok_coords = hooks['detect_button'](self.okay_button_folder)
                if ok_coords:
                    hooks['human_tap'](ok_coords[0], ok_coords[1], self.random_offset)
                    time.sleep(random.uniform(0.25, 0.5))

            # If gem dialog appears, close it and try the next upgrade button
            if self.gem_icon_folder:
                hooks['take_screenshot']()
                gem_coords = hooks['detect_button'](self.gem_icon_folder)
                if gem_coords:
                    print("💎 Gem icon detected; closing dialog (2 taps) and trying next Upgrade")
                    for _ in range(2):
                        hooks['take_screenshot']()
                        close_coords = hooks['detect_button'](self.close_button_folder)
                        if close_coords:
                            hooks['human_tap'](close_coords[0], close_coords[1], self.random_offset)
                            time.sleep(random.uniform(0.25, 0.5))
                    # Continue to next candidate
                    continue

            # No gem dialog detected after confirm/ok: treat as success
            if confirm_found:
                return True

        # No candidate produced a non-gem flow
        return False

    def perform_wall_upgrade_sequence(self, hooks: Dict[str, Callable]) -> bool:
        """Select wall and attempt up to two upgrade buttons in this selection.

        Will not attempt a third upgrade unless the wall selection process is executed again.
        """
        self.last_gem_abort = False
        if not self.open_builder_menu_and_select_wall(hooks):
            return False
        # One invocation internally tries at most two buttons
        ok = self._attempt_single_upgrade(hooks)
        time.sleep(random.uniform(0.4, 0.7))
        return ok

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

        # Keep attempting new wall selections until we see three failed selections
        failures = 0
        total_successes = 0
        while failures < 2:
            ok = self.perform_wall_upgrade_sequence(hooks)
            if ok:
                total_successes += 1
                print(f"✅ Wall upgrade selection success (total successes: {total_successes}). Attempting again…")
                time.sleep(random.uniform(0.6, 1.0))
            else:
                failures += 1
                print(f"ℹ️ Wall upgrade selection failed ({failures}/3).")
                time.sleep(random.uniform(0.6, 1.0))

        if total_successes > 0:
            print(f"✅ Wall upgrade routine done after {total_successes} success(es), 3 consecutive failures.")
        else:
            print("ℹ️ No wall upgrades applied; 3 consecutive failures.")
        self.schedule_next_wall_upgrade(current_attack_count)


