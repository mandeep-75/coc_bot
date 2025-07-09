import subprocess
import random
import cv2
import os
import glob
import time
import sys
from text_detect_resource import get_resource_values

RANDOM_OFFSET = 5  # pixels

def human_tap(base_x, base_y, offset):
    x = base_x + random.randint(-offset, offset)
    y = base_y + random.randint(-offset, offset)
    adb_command = ["adb", "shell", "input", "tap", str(x), str(y)]
    try:
        subprocess.run(adb_command, check=True)
        print(f"Tapped at ({x}, {y}) using ADB.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute ADB command: {e}")

def take_screenshot(local_path):
    try:
        cmd = f"adb exec-out screencap -p > {local_path}"
        subprocess.run(cmd, shell=True, check=True)
        print(f"Screenshot saved to {local_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to take screenshot: {e}")

def detect_button_on_screen(button_folder, screenshot_path, threshold=0.8):
    screen = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
    if screen is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return None
    template_paths = glob.glob(os.path.join(button_folder, '*'))
    if not template_paths:
        print(f"No template images found in {button_folder}")
        return None
    best_val = -1
    best_loc = None
    best_w, best_h = 0, 0
    for template_path in template_paths:
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Failed to load template: {template_path}")
            continue
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > best_val and max_val >= threshold:
            best_val = max_val
            best_loc = max_loc
            best_w, best_h = template.shape[1], template.shape[0]
    if best_loc is not None:
        center_x = best_loc[0] + best_w // 2
        center_y = best_loc[1] + best_h // 2
        print(f"Button detected at ({center_x}, {center_y}) with confidence {best_val}")
        return center_x, center_y
    else:
        print("No button detected above threshold.")
        return None

def detect_and_tap_button(button_folder, screenshot_path, threshold=0.9):
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    if coords:
        x, y = coords
        human_tap(x, y, RANDOM_OFFSET)
        return True
    else:
        print(f"No button found in {button_folder}, continuing...")
        return False

def deploy_troop_at_locations(troop_button_folder, deployment_locations, screenshot_path="screen.png"):
    if detect_and_tap_button(troop_button_folder, screenshot_path):
        random.shuffle(deployment_locations)
        print(f"Troop button clicked, deploying at {len(deployment_locations)} locations")
        for i, (x, y) in enumerate(deployment_locations):
            print(f"Deploying at location {i+1}: ({x}, {y})")
            human_tap(x, y, RANDOM_OFFSET)
            time.sleep(random.uniform(0.3, 0.5))
        return True
    else:
        print(f"Troop button not found in {troop_button_folder}")
        return False


def deploy_all_heros(hero_folder_root, hero_locations, screenshot_path="screen.png"):
    """
    Finds all hero folders inside hero_folder_root and deploys each hero at a shuffled location.
    hero_folder_root: path to the folder containing hero subfolders (e.g., 'ui_main_base/hero')
    hero_locations: list of (x, y) tuples
    """
    # Find all subfolders in hero_folder_root
    hero_folders = [os.path.join(hero_folder_root, name) for name in os.listdir(hero_folder_root)
                    if os.path.isdir(os.path.join(hero_folder_root, name))]
    shuffled_locations = hero_locations[:]
    random.shuffle(shuffled_locations)
    for folder, loc in zip(hero_folders, shuffled_locations):
        if detect_and_tap_button(folder, screenshot_path):
            print(f"Deploying hero from {folder} at {loc}")
            human_tap(loc[0], loc[1], RANDOM_OFFSET)
            time.sleep(random.uniform(0.5, 1.5))
        else:
            print(f"Hero button not found in {folder}")

def human_swipe_down(start_x=300, start_y=300, end_x=300, end_y=600, min_duration=200, max_duration=400):
    sx = start_x + random.randint(-15, 15)
    sy = start_y + random.randint(-15, 15)
    ex = end_x + random.randint(-15, 15)
    ey = end_y + random.randint(-15, 15)
    duration = random.randint(min_duration, max_duration)
    adb_command = [
        "adb", "shell", "input", "swipe",
        str(sx), str(sy), str(ex), str(ey), str(duration)
    ]
    try:
        subprocess.run(adb_command, check=True)
        print(f"Swiped down from ({sx}, {sy}) to ({ex}, {ey}) in {duration} ms.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute swipe: {e}")

# Resource thresholds (set as needed)
gold_threshold = 900000
elixir_threshold = 900000
dark_elixir_threshold = 10000

if __name__ == "__main__":
    loop_count = 0
    while True:
        try:
            loop_count += 1
            print(f"\n=== Starting Main Base Loop {loop_count} ===")
            take_screenshot("screen.png")
            detect_and_tap_button("ui_main_base/gold_collect", "screen.png")
            detect_and_tap_button("ui_main_base/eilixer_collect", "screen.png")
            detect_and_tap_button("ui_main_base/dark_eilixer_collect", "screen.png")                                  
            while True:
                take_screenshot("screen.png")
                if detect_button_on_screen("ui_main_base/attack_button", "screen.png"):
                    print("Return home button detected!")
                    break
                print("Return home button not detected yet. Waiting...")
                time.sleep(2)
            detect_and_tap_button("ui_main_base/attack_button", "screen.png")
            time.sleep(random.uniform(0.2, 0.5))
            take_screenshot("screen.png")
            detect_and_tap_button("ui_main_base/find_match_button", "screen.png")
            time.sleep(random.uniform(3.5, 4))
            take_screenshot("screen.png")
            # Resource detection and next battle loop
            attempt = 1
            while True:
                resources = get_resource_values("screen.png")
                print(f"Attempt {attempt}: Detected resources: {resources}")
                gold = int(resources.get('gold', 0) or 0)
                elixir = int(resources.get('elixir', 0) or 0)
                dark = int(resources.get('dark_elixir', 0) or 0)
                if gold >= gold_threshold or elixir >= elixir_threshold or dark >= dark_elixir_threshold:
                    print("Resource thresholds met. Proceeding with attack.")
                    break
                print("Threshold not met. Clicking next battle...")
                detect_and_tap_button("ui_main_base/next_button", "screen.png")
                time.sleep(random.uniform(5, 6))
                take_screenshot("screen.png")
                attempt += 1

            troop_locations = [
                (173, 380), (198, 395), (220, 413), (252, 438), (293, 464),
                (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
                (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
                (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
                # (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
            ]

            spell_locations = [(588, 272), (494, 395), (583, 205), (636, 395), (632, 542)]
            ice_spell_locations = [(789, 345)]

            # More strategic hero deployment positions
            hero_locations = [(149, 320), (194, 379), (214, 261), (157, 325)]

            deploy_troop_at_locations("ui_main_base/super_minion", troop_locations)
            time.sleep(random.uniform(6,7))
            deploy_troop_at_locations("ui_main_base/rage_spell", spell_locations)
            time.sleep(random.uniform(0.2, 0.5))
            # deploy_troop_at_locations("ui_main_base/ice_spell", spell_locations)
            # time.sleep(random.uniform(0.2, 0.5))
            deploy_all_heros("ui_main_base/hero", hero_locations)
            time.sleep(random.uniform(6, 8))
            detect_and_tap_button("ui_main_base/hero/grand_warden","screen.png")
            detect_and_tap_button("ui_main_base/hero/minion_prince","screen.png")
            # Wait for return home button to appear
            print("Waiting for return home button to appear...")
            while True:
                take_screenshot("screen.png")
                if detect_button_on_screen("ui_main_base/return_home", "screen.png"):
                    print("Return home button detected!")
                    break
                print("Return home button not detected yet. Waiting...")
                time.sleep(2)
            detect_and_tap_button("ui_main_base/return_home", "screen.png")
            time.sleep(random.uniform(0.2, 0.5))
            take_screenshot("screen.png")
            detect_and_tap_button("ui_main_base/okay_button", "screen.png")
            time.sleep(4)
        except Exception as e:
            print(f"Error in main base loop: {e}")
            time.sleep(2) 