from typing import Callable, Dict, List, Optional, Tuple
import random
import time
import easyocr
from difflib import SequenceMatcher


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
        self.verbose = True
        self.next_wall_upgrade_at = None
        self._ocr_reader = easyocr.Reader(['en'], gpu=gpu)
        self.ocr_region = ocr_region
        self.keywords = [k.lower() for k in (keywords or ["wall", "walls"])]
        self.target_text_region = target_text_region
        self.okay_button_folder = okay_button_folder
        self.gem_icon_folder = gem_icon_folder
        self.close_button_folder = close_button_folder

    def _tap(self, hooks: Dict[str, Callable], x: int, y: int, offset: int) -> None:
        tx = max(0, x - 10)
        ty = max(0, y - 10)
        if self.verbose:
            print(f"[TAP] ({x},{y}) -> adjusted ({tx},{ty}) offset={offset}")
        hooks['human_tap'](tx, ty, offset)

    def _normalize_text(self, s: str) -> str:
        return ''.join(ch.lower() for ch in s if ch.isalpha())

    def _similar(self, a: str, b: str) -> float:
        return SequenceMatcher(None, self._normalize_text(a), self._normalize_text(b)).ratio()

    def _prepare_ocr_image(self, img, region: Optional[Tuple[int, int, int, int]] = None):
        import cv2
        if img is None:
            return None, 1.0, (0, 0)
        if region is not None:
            x1, y1, x2, y2 = region
            img = img[y1:y2, x1:x2]
            offset = (x1, y1)
        else:
            offset = (0, 0)
        # upscale to help OCR small text
        h, w = img.shape[:2]
        scale = 1.5 if max(h, w) < 1200 else 1.2
        img_resized = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
        # convert to gray
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        # contrast-limited adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        # gentle denoise while preserving edges
        gray = cv2.bilateralFilter(gray, d=5, sigmaColor=50, sigmaSpace=50)
        # adaptive threshold to emphasize text
        th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 5)
        return th, scale, offset

    def _readtext_multi(self, img, region: Optional[Tuple[int, int, int, int]] = None):
        # Return absolute screen-space centers with text/confidence
        import cv2
        results_abs: List[Tuple[int, int, str, float]] = []
        proc_img, scale, offset = self._prepare_ocr_image(img, region)
        if proc_img is not None:
            proc_res = self._ocr_reader.readtext(proc_img)
            if self.verbose:
                print(f"[OCR] processed crop results: {[(t, round(c,2)) for (_, t, c) in proc_res]}")
            for (bbox, text, conf) in proc_res:
                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]
                cx = int(sum(xs) / 4 / scale) + offset[0]
                cy = int(sum(ys) / 4 / scale) + offset[1]
                results_abs.append((cx, cy, text, conf))
        # Original crop
        crop_orig = img
        off2 = (0, 0)
        if region is not None and crop_orig is not None:
            x1, y1, x2, y2 = region
            crop_orig = crop_orig[y1:y2, x1:x2]
            off2 = (x1, y1)
        if crop_orig is not None:
            orig_res = self._ocr_reader.readtext(crop_orig)
            if self.verbose:
                print(f"[OCR] original crop results: {[(t, round(c,2)) for (_, t, c) in orig_res]}")
            for (bbox, text, conf) in orig_res:
                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]
                cx = int(sum(xs) / 4) + off2[0]
                cy = int(sum(ys) / 4) + off2[1]
                results_abs.append((cx, cy, text, conf))
        return results_abs

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
        results = self._readtext_multi(img, region)
        needle_lower = needle_text.lower()
        for (cx, cy, text, _conf) in results:
            if text and (needle_lower in text.lower() or self._similar(text, needle_text) >= 0.7):
                if self.verbose:
                    print(f"[OCR] match '{text}' ~ '{needle_text}' at ({cx},{cy}) region={region}")
                return (cx, cy)
        return None

    def _human_swipe(self, hooks: Dict[str, Callable], sx: int, sy: int, ex: int, ey: int) -> None:
        import subprocess
        device_id = hooks['device_id']
        duration = random.randint(80, 140)
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
        time.sleep(random.uniform(0.25, 0.45))

        for _ in range(8):
            time.sleep(random.uniform(0.1, 0.2))
            hooks['take_screenshot']()
            for kw in self.keywords:
                center = self._find_text_center_on_screen(kw, hooks, region=self.ocr_region)
                if center:
                    print(f"🔎 Found '{kw}' at {center}. Attempting precise taps to select wall…")
                    # Try a small cluster of taps around the detected center; no random offset
                    probe_offsets = [
                        (0, 0), (-10, -10), (10, 0), (0, 10), (-10, 0), (0, -10), (10, 10), (-10, 10)
                    ]
                    for dx, dy in probe_offsets:
                        px = max(0, center[0] + dx)
                        py = max(0, center[1] + dy)
                        print(f"[WALL] probing tap at ({px},{py}) (dx={dx}, dy={dy})")
                        hooks['human_tap'](px, py, 0)
                        time.sleep(random.uniform(0.12, 0.2))
                        # Verify selection by checking for Upgrade text in the expected region
                        hooks['take_screenshot']()
                        maybe_upgrade = self._find_text_center_on_screen("upgrade", hooks, region=self.target_text_region)
                        if maybe_upgrade:
                            print(f"[WALL] selection confirmed (found Upgrade at {maybe_upgrade})")
                            time.sleep(random.uniform(0.12, 0.2))
                            return True
                    print("[WALL] probes did not confirm selection; continuing scroll/search…")
            self._human_swipe(hooks, 830, 470, 830, 270)
        print("⚠️ 'Wall' not found in builder menu after scrolling.")
        return False

    def _attempt_single_upgrade(self, hooks: Dict[str, Callable]) -> bool:
        import cv2
        time.sleep(random.uniform(0.1, 0.2))

        # Collect all candidate Upgrade buttons by OCR with fuzzy match
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

        results = self._readtext_multi(img, region)
        candidates: List[Tuple[int, int]] = []
        for (cx, cy, text, _conf) in results:
            if not text:
                continue
            if ("upgrade" in text.lower()) or (self._similar(text, "upgrade") >= 0.68) or ("@pgrade" in text.lower()):
                candidates.append((cx, cy))
                if self.verbose:
                    print(f"[UPGRADE] candidate '{text}' -> ({cx},{cy}) region={region}")

        # Consider only the last two upgrade buttons per selection (tap from the end)
        candidates = candidates[-2:]

        # Toggle between last and second-last if gem dialog appears
        ordered = list(reversed(candidates))  # [last, second-last]
        if self.verbose:
            print(f"[UPGRADE] ordered candidates: {ordered}")
        toggle_index = 0
        max_attempts = 6  # safety cap to avoid infinite loops
        attempt = 0
        while attempt < max_attempts and ordered:
            ux, uy = ordered[toggle_index % len(ordered)]
            print(f"✅ Upgrade attempt {attempt+1}: tapping at ({ux}, {uy})")
            hooks['human_tap'](ux, uy, self.random_offset)
            time.sleep(random.uniform(0.1, 0.2))

            # Try to find and tap confirm
            confirm_found = False
            for _ in range(3):
                hooks['take_screenshot']()
                center = None
                for tkn in ("Confirm", "Coufian", "Confian"):
                    center = self._find_text_center_on_screen(tkn, hooks, region=self.target_text_region)
                    if center:
                        break
                if center:
                    print(f"✅ Found Confirm at {center} (token={tkn}); tapping")
                    hooks['human_tap'](center[0], center[1], self.random_offset)
                    confirm_found = True
                    time.sleep(random.uniform(0.1, 0.2))
                    break
                time.sleep(0.25)

            # Tap any OK dialog if present (not the gem icon)
            if self.okay_button_folder:
                hooks['take_screenshot']()
                ok_coords = hooks['detect_button'](self.okay_button_folder)
                if ok_coords:
                    if self.verbose:
                        print(f"[OK] dialog detected at {ok_coords}")
                    hooks['human_tap'](ok_coords[0], ok_coords[1], self.random_offset)
                    time.sleep(random.uniform(0.08, 0.15))

            # If gem dialog appears, close it and toggle to the other upgrade button
            if self.gem_icon_folder:
                hooks['take_screenshot']()
                gem_coords = hooks['detect_button'](self.gem_icon_folder)
                if gem_coords:
                    print(f"💎 Gem icon detected at {gem_coords}; closing dialog (2 taps) and toggling to other Upgrade")
                    for _ in range(2):
                        hooks['take_screenshot']()
                        close_coords = hooks['detect_button'](self.close_button_folder)
                        if close_coords:
                            print(f"[CLOSE] tapping close at {close_coords}")
                            hooks['human_tap'](close_coords[0], close_coords[1], self.random_offset)
                            time.sleep(random.uniform(0.08, 0.15))
                    attempt += 1
                    toggle_index += 1  # flip between last and second-last
                    time.sleep(random.uniform(0.1, 0.2))
                    continue

            # No gem dialog detected after confirm/ok: treat as success
            if confirm_found:
                return True

            # If neither confirm nor gem appeared, break (nothing to do)
            attempt += 1
            toggle_index += 1

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
        time.sleep(random.uniform(0.15, 0.3))
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
        time.sleep(random.uniform(0.1, 0.2))

        # Keep attempting new wall selections until we see three failed selections
        failures = 0
        total_successes = 0
        while failures < 2:
            ok = self.perform_wall_upgrade_sequence(hooks)
            if ok:
                total_successes += 1
                print(f"✅ Wall upgrade selection success (total successes: {total_successes}). Attempting again…")
                time.sleep(random.uniform(0.2, 0.4))
            else:
                failures += 1
                print(f"ℹ️ Wall upgrade selection failed ({failures}/3).")
                time.sleep(random.uniform(0.2, 0.4))

        if total_successes > 0:
            print(f"✅ Wall upgrade routine done after {total_successes} success(es), 3 consecutive failures.")
        else:
            print("ℹ️ No wall upgrades applied; 3 consecutive failures.")
        self.schedule_next_wall_upgrade(current_attack_count)


