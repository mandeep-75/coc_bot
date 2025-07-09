import subprocess
import random
import cv2
import os
import glob
import time
troop_folder = "ui_builder_base/witch"
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
    """
    Takes a screenshot on the connected Android device and saves it directly to the local machine using adb exec-out.
    local_path: where to save the screenshot locally
    """
    try:
        cmd = f"adb exec-out screencap -p > {local_path}"
        subprocess.run(cmd, shell=True, check=True)
        print(f"Screenshot saved to {local_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to take screenshot: {e}")

def detect_button_on_screen(button_folder, screenshot_path, threshold=0.8):
    """
    Detects a button on the screen using template matching with all images in the given folder.
    Returns the (x, y) center coordinates of the best match if found, else None.
    """
  

    screen = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
    if screen is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return None

    # Get all image files in the button_folder
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
    """
    Detects a button and taps it if found. Returns True if button was tapped, False otherwise.
    """
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    if coords:
        x, y = coords
        human_tap(x, y, RANDOM_OFFSET)
        return True
    else:
        print(f"No button found in {button_folder}, continuing...")
        return False



def deploy_troops_at_detected_areas(area_folder, screenshot_path):
    """
    Detects deployment areas using template matching and deploys troops there.
    area_folder: folder containing images of deployment areas
    """
    coords = detect_button_on_screen(area_folder, screenshot_path, threshold=0.9)
    if coords:
        x, y = coords
        print(f"Deploying troop at detected area ({x}, {y})")
        human_tap(x, y, RANDOM_OFFSET)
        return True
    else:
        print("No deployment area detected")
        return False

def deploy_troop_at_locations(troop_button_folder, deployment_locations, screenshot_path="screen.png"):
    """
    Clicks a troop button and deploys at predefined locations.
    troop_button_folder: folder containing troop button images
    deployment_locations: list of (x, y) coordinates for deployment
    """
    # First, click the troop button
    if detect_and_tap_button(troop_button_folder, screenshot_path):
        print(f"Troop button clicked, deploying at {len(deployment_locations)} locations")
        
        # Deploy at each predefined location
        for i, (x, y) in enumerate(deployment_locations):
            print(f"Deploying at location {i+1}: ({x}, {y})")
            human_tap(x, y, RANDOM_OFFSET)
            time.sleep(random.uniform(0.5, 1.5))
        return True
    else:
        print(f"Troop button not found in {troop_button_folder}")
        return False

def human_swipe_down(start_x=300, start_y=300, end_x=300, end_y=600, min_duration=200, max_duration=400):
    """
    Performs a human-like swipe down gesture using adb.
    The start/end points and duration are randomized within reasonable bounds.
    """
    # Add randomness to start/end points
    sx = start_x + random.randint(-15, 15)
    sy = start_y + random.randint(-15, 15)
    ex = end_x + random.randint(-15, 15)
    ey = end_y + random.randint(-15, 15)
    duration = random.randint(min_duration, max_duration)  # milliseconds
    adb_command = [
        "adb", "shell", "input", "swipe",
        str(sx), str(sy), str(ex), str(ey), str(duration)
    ]
    try:
        subprocess.run(adb_command, check=True)
        print(f"Swiped down from ({sx}, {sy}) to ({ex}, {ey}) in {duration} ms.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute swipe: {e}")


if __name__ == "__main__":
    loop_count = 0
    while True:
        try:
            loop_count += 1
            print(f"\n=== Starting Loop {loop_count} ===")
            take_screenshot("screen.png")
            detect_and_tap_button("ui_builder_base/attack_button", "screen.png")
            time.sleep(random.uniform(0.2, 0.5))
            take_screenshot("screen.png")
            detect_and_tap_button("ui_builder_base/find_match_button", "screen.png")
            time.sleep(random.uniform(0.2, 0.5))
            take_screenshot("screen.png")
            deployment_locations = [
                (50, 360), 
            ]
            deploy_troop_at_locations("ui_builder_base/battle_mechine", deployment_locations)
            deployment_locations2 = [
                (50, 360), 
                (300, 200), 
                (160, 260),  
                (190, 400), 
                (160, 260),  
                (190, 400), 
                (190, 400), 
            ]

            deploy_troop_at_locations(troop_folder, deployment_locations2)
            time.sleep(random.uniform(0.2, 0.5))  # Wait before starting next loop
            deploy_troop_at_locations("ui_builder_base/battle_mechine", deployment_locations)
            deploy_troop_at_locations(troop_folder, deployment_locations2)
            time.sleep(random.uniform(0.2, 0.5))  # Wait before starting next loop
            take_screenshot("screen.png")
            detect_and_tap_button("ui_builder_base/return_home", "screen.png")
            time.sleep(random.uniform(0.2, 0.5))
            take_screenshot("screen.png")
            detect_and_tap_button("ui_builder_base/okay_button", "screen.png")
            detect_and_tap_button("ui_builder_base/gold", "screen.png")
            time.sleep(random.uniform(0.1,0.5))
            detect_and_tap_button("ui_builder_base/eilixer", "screen.png")
            time.sleep(random.uniform(0.2, 0.5))
            print(f"=== Completed Loop {loop_count} ===")
            
        except KeyboardInterrupt:
            print("\nBot stopped by user (Ctrl+C)")
            break
        except Exception as e:
            print(f"Error in loop {loop_count}: {e}")
            time.sleep(5)  # Wait before retrying
            continue
    
  
  