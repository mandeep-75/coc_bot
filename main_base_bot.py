import subprocess
import random
import cv2
import os
import glob
import time
from utils.text_detect_resource import get_resource_values

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
selected_device = None
last_resources = None

# Screenshot file used everywhere
SCREENSHOT_NAME = "screen.png"

# Log file for tracking progress
LOG_FILE = "bot_session_log.txt"

# Session totals
session_gold = 0
session_elixir = 0
session_dark = 0
average_gold = session_gold/5
average__elixir = session_elixir/5
average_dark = session_dark/5
# =============================================================================
# CONFIGURATION
# =============================================================================

# Random offsets for human-like randomness
RANDOM_OFFSET = 3
RANDOM_OFFSET_HEROES = 3
RANDOM_OFFSET_SPELLS = 25

# Resource thresholds for selecting bases
gold_threshold = 1000000
elixir_threshold = 1000000
dark_elixir_threshold = 0
max_trophies_attack_threshold = 30

# =============================================================================
# DEPLOYMENT COORDINATES
# =============================================================================

troop_locations = [
    (173, 380), (198, 395), (220, 413), (252, 438), (293, 464),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
    (227, 258), (256, 230), (293, 464)
]

spell_locations = [
    (588, 272), (494, 395), (583, 205), (636, 395), (632, 500)
]

ice_spell_locations = [(789, 345)]

hero_locations = [
    (149, 320), (194, 379), (214, 261), (157, 325), (214, 261)
]

# =============================================================================
# DEVICE & INTERACTION FUNCTIONS
# =============================================================================

def select_devices():
    """Lists connected Android devices and allows selection.
       Automatically selects the only device if just one is available."""
    adb_command = ["adb", "devices"]

    try:
        result = subprocess.run(adb_command, capture_output=True, text=True, check=True)
        # Parse connected device IDs
        devices = [line.split('\t')[0] for line in result.stdout.strip().split('\n')[1:] if line.strip() and '\tdevice' in line]

        if not devices:
            print("❌ No devices connected.")
            return None

        # Auto-select if only one device
        if len(devices) == 1:
            print(f"✅ One device detected: {devices[0]} (auto-selected)")
            return devices[0]

        # Otherwise, list options
        print("📱 Connected devices:")
        for i, device in enumerate(devices):
            print(f"{i + 1}: {device}")

        choice = input("Select a device by number (or press Enter for first): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(devices):
            selected = devices[int(choice) - 1]
        else:
            selected = devices[0]

        print(f"✅ Selected device: {selected}")
        return selected

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to execute ADB command: {e}")
        return None

def human_tap(base_x, base_y, offset):
    """Simulates human-like tapping with random offset."""
    x = base_x + random.randint(-offset, offset)
    y = base_y + random.randint(-offset, offset)
    cmd = ["adb", "-s", selected_device, "shell", "input", "tap", str(x), str(y)]
    try:
        subprocess.run(cmd, check=True)
        print(f"Tapped at ({x}, {y})")
    except subprocess.CalledProcessError as e:
        print(f"Failed to tap: {e}")


def take_screenshot(local_path=SCREENSHOT_NAME):
    """Captures a screenshot from the device."""
    try:
        cmd = f"adb -s {selected_device} exec-out screencap -p > {local_path}"
        subprocess.run(cmd, shell=True, check=True)
        print(f"Screenshot saved: {local_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to take screenshot: {e}")


def detect_button_on_screen(button_folder, screenshot_path=SCREENSHOT_NAME, threshold=0.8):
    """Detects a button on screen using template matching."""
    screen = cv2.imread(screenshot_path)
    if screen is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return None

    template_paths = glob.glob(os.path.join(button_folder, '*'))
    if not template_paths:
        print(f"No templates in {button_folder}")
        return None

    best_val, best_loc, best_w, best_h = -1, None, 0, 0
    for template_path in template_paths:
        template = cv2.imread(template_path)
        if template is None:
            continue
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val > best_val and max_val >= threshold:
            best_val, best_loc = max_val, max_loc
            best_w, best_h = template.shape[1], template.shape[0]

    if best_loc:
        x, y = best_loc[0] + best_w // 2, best_loc[1] + best_h // 2
        print(f"Button detected ({x},{y}) conf={best_val*100:.1f}%")
        return x, y
    return None


def detect_and_tap_button(button_folder, screenshot_path=SCREENSHOT_NAME, threshold=0.9):
    """Detects a button and taps it."""
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    # print(f"Detect and tap button in {button_folder}: {'Found' if coords else 'Not found'}")
    if coords:
        human_tap(*coords, RANDOM_OFFSET)
        return True
    return False


def detect_and_tap_button_precise(button_folder, screenshot_path=SCREENSHOT_NAME, threshold=0.8):
    """Precise tapping for heroes."""
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    if coords:
        human_tap(*coords, RANDOM_OFFSET_HEROES)
        return True
    return False


# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================

def deploy_troop_at_locations(troop_button_folder, locations, units):
    """Deploys troops in human-like manner."""
    if not detect_and_tap_button(troop_button_folder):
        print(f"Troop not found in: {troop_button_folder}")
        return False

    random.shuffle(locations)
    coords = [locations[i % len(locations)] for i in range(units)]
    random.shuffle(coords)

    print(f"Deploying {units} troops...")
    for i, (x, y) in enumerate(coords):
        human_tap(x, y, RANDOM_OFFSET)
        print(f"Troop {i + 1}/{units} at ({x},{y})")
        time.sleep(random.uniform(0.3, 0.5))
    return True


def deploy_spells_at_locations(spell_button_folder, locations):
    """Deploys spells with area offset."""
    if not detect_and_tap_button(spell_button_folder):
        print(f"Spell not found in: {spell_button_folder}")
        return False

    random.shuffle(locations)
    for (x, y) in locations:
        human_tap(x, y, RANDOM_OFFSET_SPELLS)
        time.sleep(random.uniform(0.3, 0.5))
    return True


def deploy_all_heroes(hero_folder_root, hero_locations):
    """Deploys all available heroes."""
    hero_folders = [os.path.join(hero_folder_root, h) for h in os.listdir(hero_folder_root)
                    if os.path.isdir(os.path.join(hero_folder_root, h))]

    random.shuffle(hero_folders)
    random.shuffle(hero_locations)

    for folder, loc in zip(hero_folders, hero_locations):
        if detect_and_tap_button_precise(folder):
            human_tap(loc[0], loc[1], RANDOM_OFFSET_HEROES)
            time.sleep(random.uniform(0.5, 1.5))


# =============================================================================
# MAIN BOT LOOP
# =============================================================================

if __name__ == "__main__":
    loop_count = 0
    start_time = time.time()

    # Start session log
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n===== NEW BOT SESSION STARTED =====\n")
        f.write(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    while True:
        try:
            loop_count += 1
            print(f"\n=== MAIN LOOP {loop_count} START ===")

            # Step 0: Connect device
            if selected_device is None:
                selected_device = select_devices()

            # Step 1: Collect resources
            take_screenshot()
            detect_and_tap_button("ui_main_base/gold_collect")
            detect_and_tap_button("ui_main_base/elixir_collect")
            detect_and_tap_button("ui_main_base/dark_elixir_collect")


            # Step 2: Open attack menu
            while True:
                take_screenshot(SCREENSHOT_NAME)
                coords = detect_button_on_screen("ui_main_base/attack_button", SCREENSHOT_NAME)
                if coords:
                    print("Attack button found — tapping.")
                    human_tap(*coords, RANDOM_OFFSET)
                    break
                print("Waiting for Attack button...")
                time.sleep(2)

            # Step 3: Find match
            while True:
                take_screenshot(SCREENSHOT_NAME)
                coords = detect_button_on_screen("ui_main_base/find_match_button", SCREENSHOT_NAME)
                if coords:
                    print("Find Match button found — tapping.")
                    human_tap(*coords, RANDOM_OFFSET)
                    break
                else:
                    detect_and_tap_button("ui_main_base/okay_button")
                    detect_and_tap_button("ui_main_base/attack_button")
                    print("Waiting for Find Match...")
                time.sleep(2)


            # Step 4: Search for suitable base
            take_screenshot()
            attempt = 1

            while True:
                resources = get_resource_values(SCREENSHOT_NAME)
                gold = resources.get('gold', 0)
                elixir = resources.get('elixir', 0)
                dark = resources.get('dark_elixir', 0)

                if last_resources == resources or (gold == 0 and elixir == 0 and dark == 0):
                    print(f"Attempt {attempt}: (duplicate/zero loot) skipped.")
                else:
                    print(f"Attempt {attempt}: Resources found: {resources}")

                last_resources = resources.copy()

                if (gold >= gold_threshold or elixir >= elixir_threshold) and dark >= dark_elixir_threshold:
                    print("✅ Suitable base found. Proceeding to attack.")
                    session_gold += gold
                    session_elixir += elixir
                    session_dark += dark

                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Attack {loop_count}: Gold={gold:,}, Elixir={elixir:,}, Dark={dark:,}\n")
                    break

                print("❌ Base not suitable. Searching next...")
                detect_and_tap_button("ui_main_base/next_button")
                time.sleep(random.uniform(4.5, 5))
                take_screenshot()
                attempt += 1

            # Step 5: Deploy troops
            deploy_troop_at_locations("ui_main_base/troops/super_minion", troop_locations, 28)
            time.sleep(random.uniform(6, 7))

            # Step 6: Deploy heroes
            deploy_all_heroes("ui_main_base/hero", hero_locations)

            # Step 7: Deploy spells
            deploy_spells_at_locations("ui_main_base/spells/rage", spell_locations)
            time.sleep(random.uniform(6, 8))

            # Step 8: Activate hero abilities
            detect_and_tap_button("ui_main_base/hero/grand_warden")
            detect_and_tap_button("ui_main_base/hero/minion_prince")

            # Step 9: Wait for return home
            print("Waiting for 'Return Home'...")
            while not detect_button_on_screen("ui_main_base/return_home"):
                time.sleep(random.uniform(3, 3.5))
                take_screenshot()

            detect_and_tap_button("ui_main_base/return_home")
            time.sleep(random.uniform(4, 4.5))
            detect_and_tap_button("ui_main_base/okay_button")

            # Step 10: Write progress summary every 5 attacks
            if loop_count % 5 == 0:
                elapsed = (time.time() - start_time) / 60
                summary = (
                    f"\n===== SESSION SUMMARY =====\n"
                    f"Attacks: {loop_count}\n"
                    f"Average Gold: {average_gold:,}\n"
                    f"Average Elixir: {average__elixir:,}\n"
                    f"Average Dark: {average_dark:,}\n"
                    f"Runtime: {elapsed:.1f} mins\n"
                    f"============================\n"
                )
                print(summary)
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(summary)

        except Exception as e:
            print(f"⚠️ Error in loop: {e}")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"⚠️ Error in loop {loop_count}: {str(e)}\n")
            time.sleep(2)
