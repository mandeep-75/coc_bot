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
average_gold = 0
average_elixir = 0
average_dark = 0

# =============================================================================
# CONFIGURATION
# =============================================================================
RANDOM_OFFSET = 3
RANDOM_OFFSET_HEROES = 3
RANDOM_OFFSET_SPELLS = 25

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

hero_locations = [
    (149, 320), (194, 379), (214, 261), (157, 325), (214, 261)
]

# =============================================================================
# DEVICE & INTERACTION FUNCTIONS
# =============================================================================
def select_devices():
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
        choice = input("Select a device by number (or press Enter for first): ").strip()
        selected = devices[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(devices) else devices[0]
        print(f"✅ Selected device: {selected}")
        return selected
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to execute ADB command: {e}")
        return None

def human_tap(base_x, base_y, offset):
    x = base_x + random.randint(-offset, offset)
    y = base_y + random.randint(-offset, offset)
    cmd = ["adb", "-s", selected_device, "shell", "input", "tap", str(x), str(y)]
    try:
        subprocess.run(cmd, check=True)
        print(f"Tapped at ({x}, {y})")
    except subprocess.CalledProcessError as e:
        print(f"Failed to tap: {e}")

def take_screenshot(local_path=SCREENSHOT_NAME):
    try:
        cmd = f"adb -s {selected_device} exec-out screencap -p > {local_path}"
        subprocess.run(cmd, shell=True, check=True)
        print(f"Screenshot saved: {local_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to take screenshot: {e}")

def detect_button_on_screen(button_folder, screenshot_path=SCREENSHOT_NAME, threshold=0.8):
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

def detect_and_tap_button(button_folder, screenshot_path=SCREENSHOT_NAME, threshold=0.8):
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    if coords:
        human_tap(*coords, RANDOM_OFFSET)
        return True
    return False

def detect_and_tap_button_precise(button_folder, screenshot_path=SCREENSHOT_NAME, threshold=0.8):
    """
    Precise tapping for heroes. Returns coordinates if found, else None.
    """
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    if coords:
        human_tap(*coords, RANDOM_OFFSET_HEROES)
        return coords  # ✅ Return the (x, y) tuple instead of True
    return None  # ❌ Not found


# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================
def deploy_troop_at_locations(troop_button_folder, locations, units):
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
        time.sleep(random.uniform(0.1, 0.3))
    return True

def deploy_spells_at_locations(spell_button_folder, locations):
    if not detect_and_tap_button(spell_button_folder):
        print(f"Spell not found in: {spell_button_folder}")
        return False
    random.shuffle(locations)
    for (x, y) in locations:
        human_tap(x, y, RANDOM_OFFSET_SPELLS)
        time.sleep(random.uniform(0.3, 0.5))
    return True

# =============================================================================
# HERO DEPLOYMENT + RETAP LOGIC (By Name)
# =============================================================================

# Global dictionary to store deployed hero coordinates
deployed_heroes = {}  # e.g. {"grand_warden": (x, y), "barbarian_king": (x, y)}

def deploy_all_heroes(hero_folder_root, hero_locations):
    global deployed_heroes
    deployed_heroes = {}

    hero_folders = [
        os.path.join(hero_folder_root, h)
        for h in os.listdir(hero_folder_root)
        if os.path.isdir(os.path.join(hero_folder_root, h))
    ]

    random.shuffle(hero_folders)
    random.shuffle(hero_locations)

    for folder, loc in zip(hero_folders, hero_locations):
        hero_name = os.path.basename(folder).lower()
        coords = detect_and_tap_button_precise(folder)

        if coords:  # ✅ coords is now a tuple, not a bool
            print(f"🦸 Deploying {hero_name} at {loc}")
            human_tap(loc[0], loc[1], RANDOM_OFFSET_HEROES)
            deployed_heroes[hero_name] = coords
            time.sleep(random.uniform(0.5, 1.5))
        else:
            print(f"⚠️ {hero_name} not found on screen")

    print(f"✅ Stored hero coordinates: {deployed_heroes}")



def retap_hero_by_name(hero_name):
    """
    Retaps a specific hero (by name) to trigger its ability.
    Example: retap_hero_by_name('grand_warden')
    """
    global deployed_heroes
    hero_name = hero_name.lower()

    if hero_name not in deployed_heroes:
        print(f"⚠️ Hero '{hero_name}' not found in stored coordinates.")
        return

    x, y = deployed_heroes[hero_name]
    print(f"⚔️ Retapping {hero_name} at ({x}, {y})")
    human_tap(x, y, RANDOM_OFFSET_HEROES)
    time.sleep(random.uniform(0.4, 0.8))


def retap_all_heroes():
    """
    Retaps all previously deployed heroes (activates all abilities).
    """
    global deployed_heroes

    if not deployed_heroes:
        print("⚠️ No stored heroes to retap.")
        return

    print(f"⚔️ Retapping all {len(deployed_heroes)} heroes...")
    for hero_name, (x, y) in deployed_heroes.items():
        print(f"✨ Activating {hero_name} ability...")
        human_tap(x, y, RANDOM_OFFSET_HEROES)
        time.sleep(random.uniform(0.4, 0.8))

    print("✅ All hero abilities triggered successfully.")


# =============================================================================
# MAIN BOT LOOP
# =============================================================================
if __name__ == "__main__":
    loop_count = 0
    start_time = time.time()

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

            # Step 2: Wait for Attack button (max 3:30)
            start_wait = time.time()
            while True:
                if time.time() - start_wait > 30:
                    print("⏭️ Timeout waiting for Attack button. Skipping this step.")
                    break
                take_screenshot(SCREENSHOT_NAME)
                coords = detect_button_on_screen("ui_main_base/attack_button", SCREENSHOT_NAME)
                if coords:
                    print("Attack button found — tapping.")
                    human_tap(*coords, RANDOM_OFFSET)
                    break
                print("Waiting for Attack button...")
                time.sleep(2)

            # Step 3: Wait for Find Match 
            start_wait = time.time()
            while True:
                if time.time() - start_wait > 30:
                    print("⏭️ Timeout waiting for Find Match button. Skipping attack.")
                    break
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

            # Step 4: Search for suitable base ( timeout, reset on 'Next')
            take_screenshot()
            attempt = 1
            search_start = time.time()

            while True:
                if time.time() - search_start > 120:
                    print("⏭️ Timeout searching for base (no progress). Skipping attack.")
                    break

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
                if detect_and_tap_button("ui_main_base/next_button"):
                    print("➡️ Next button found — resetting base search timer.")
                    search_start = time.time()  # Reset timeout
                else:
                    print("⚠️ Next button not found — timer continues.")

                time.sleep(random.uniform(4.5, 5))
                take_screenshot()
                attempt += 1

            # Step 5: Deploy troops, heroes, spells
            deploy_troop_at_locations("ui_main_base/troops/super_minion", troop_locations, 24)
            time.sleep(random.uniform(6, 7))
            deploy_all_heroes("ui_main_base/hero", hero_locations)
            deploy_spells_at_locations("ui_main_base/spells/rage", spell_locations)
            time.sleep(random.uniform(6, 8))
            retap_hero_by_name('grand_warden')

            # Step 6: Wait for Return Home
            print("Waiting for 'Return Home'...")
            home_wait_start = time.time()
            while True:
                if time.time() - home_wait_start > 210:
                    print("⏭️ Timeout waiting for Return Home. Skipping to next loop.")
                    break
                if detect_button_on_screen("ui_main_base/return_home"):
                    detect_and_tap_button("ui_main_base/return_home")
                    time.sleep(random.uniform(4, 4.5))
                    detect_and_tap_button("ui_main_base/okay_button")
                    break
                if time.time() - home_wait_start > random.uniform(10, 20):
                    print("Force Quitting match")
                    take_screenshot()
                    detect_and_tap_button("ui_main_base/end_battle")
                    detect_and_tap_button("ui_main_base/surrender_button")
                    take_screenshot()
                    detect_and_tap_button("ui_main_base/okay_button")
                    take_screenshot
                    detect_and_tap_button("ui_main_base/return_home")

                time.sleep(random.uniform(3, 3.5))
                take_screenshot()

            # Step 7: Summary every 5 attacks
            if loop_count % 5 == 0:
                elapsed = (time.time() - start_time) / 60
                average_gold = session_gold / loop_count if loop_count > 0 else 0
                average_elixir = session_elixir / loop_count if loop_count > 0 else 0
                average_dark = session_dark / loop_count if loop_count > 0 else 0
                summary = (
                    f"\n===== SESSION SUMMARY =====\n"
                    f"Attacks: {loop_count}\n"
                    f"Average Gold: {average_gold:,}\n"
                    f"Average Elixir: {average_elixir:,}\n"
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
