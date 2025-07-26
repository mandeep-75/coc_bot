import subprocess
import random
import cv2
import os
import glob
import time
from utils.text_detect_resource import get_resource_values
# =============================================================================
selected_device = None
# =============================================================================
# CONFIGURATION SECTION - EASY TO MODIFY FOR NEW USERS
# =============================================================================

# Random offset settings for different types of interactions
# These add human-like randomness to prevent detection
RANDOM_OFFSET = 3         # For regular troop deployments
RANDOM_OFFSET_HEROES = 3   # For hero deployments (more precise)
RANDOM_OFFSET_SPELLS = 100 # For spell deployments (larger area)

# Resource thresholds for base selection
# Only attack bases that have at least these resources
gold_threshold = 50000        # Minimum gold required
elixir_threshold = 50000     # Minimum elixir required  
dark_elixir_threshold = 0      # Minimum dark elixir required
max_trophies_attack_threshold = 30  # Maximum trophies to attack

# =============================================================================
# DEPLOYMENT LOCATIONS - CUSTOMIZE YOUR ATTACK STRATEGY
# =============================================================================

# Troop deployment coordinates (x, y) on the screen
# Add more coordinates for more deployment points
# Coordinates are shuffled for randomness
troop_locations = [
    (173, 380), (198, 395), (220, 413), (252, 438), (293, 464),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
    (321, 479), (178, 288), (203, 271), (227, 258), (256, 230),
    (295, 202), (318, 188), (357, 166), (383, 144), (406, 120),
   # (227, 258), (256, 230),(293, 464),  # Commented out coordinates
]

# Spell deployment coordinates
# Spells are deployed with larger random offset for area coverage
spell_locations = [
    (588, 272), (494, 395), (583, 205), (636, 395), (632, 500)
]

# Ice spell specific locations (if different from regular spells)
ice_spell_locations = [
    (789, 345)
]

# Hero deployment coordinates
# Must match the number of heroes you have available
# Each hero gets one coordinate, coordinates are shuffled
hero_locations = [
    (149, 320), (194, 379), (214, 261), (157, 325),(214, 261)
]

# =============================================================================
# CORE FUNCTIONS
# =============================================================================
def select_devices():
    """
    Lists connected Android devices and allows user to select one.
    
    Returns:
        Selected device ID or None if no devices found.
    """
    adb_command = ["adb", "devices"]
    try:
        result = subprocess.run(adb_command, capture_output=True, text=True, check=True)
        devices = result.stdout.strip().split('\n')[1:]  # Skip the first line (header)
        devices = [line.split('\t')[0] for line in devices if line.strip()]
        
        if not devices:
            print("No devices connected.")
            return None
        
        print("Connected devices:")
        for i, device in enumerate(devices):
            print(f"{i + 1}: {device}")
        
        choice = input("Select a device by number (or press Enter for first): ")
        if choice.isdigit() and 1 <= int(choice) <= len(devices):
            return devices[int(choice) - 1]
        else:
            return devices[0]  # Default to first device
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute ADB command: {e}")
        return None

        
def human_tap(base_x, base_y, offset):
    """
    Simulates human-like tapping with random offset.
    
    Args:+++
        base_x, base_y: Base coordinates to tap
        offset: Random offset range for human-like behavior
    """
    x = base_x + random.randint(-offset, offset)
    y = base_y + random.randint(-offset, offset)

    adb_command = ["adb","-s",selected_device,"shell", "input", "tap", str(x), str(y)]
    try:
        subprocess.run(adb_command, check=True)
        print(f"Tapped at ({x}, {y})")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute ADB command: {e}")

def take_screenshot(local_path):
    """
    Takes a screenshot of the connected Android device.
    
    Args:
        local_path: Where to save the screenshot
    """
    try:
        #s cmd = f"adb exec-out screencap -p > {local_path}"
        cmd = f"adb -s {selected_device} exec-out screencap -p > {local_path}"
        subprocess.run(cmd, shell=True, check=True)
        print(f"Screenshot saved to {local_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to take screenshot: {e}")

def detect_button_on_screen(button_folder, screenshot_path, threshold=0.8):
    """
    Detects if a button (from button_folder) is present on the screen.
    
    Args:
        button_folder: Folder containing button template images
        screenshot_path: Path to current screenshot
        threshold: Confidence threshold (0.0-1.0) for detection
    
    Returns:
        (x, y) coordinates of button center, or None if not found
    """
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
        print(f"Button detected at ({center_x}, {center_y}) with confidence {best_val*100}")
        return center_x, center_y
    else:
        print(f"No button detected above threshold from all images in folder:{button_folder}")
        return None

def detect_and_tap_button(button_folder, screenshot_path, threshold=0.9):
    """
    Detects a button and taps it if found.
    
    Args:
        button_folder: Folder containing button template images
        screenshot_path: Path to current screenshot
        threshold: Confidence threshold for detection
    
    Returns:
        True if button was found and tapped, False otherwise
    """
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    if coords:
        x, y = coords
        human_tap(x, y, RANDOM_OFFSET)
        return True
    else:
        print(f"No button found in ui form folder: {button_folder}, continuing...")
        return False
    
def detect_and_tap_button_precise(button_folder, screenshot_path, threshold=0.8):
    """
    More accurate button detection and tapping for heroes.
    Uses smaller random offset for precision.
    
    Args:
        button_folder: Folder containing button template images
        screenshot_path: Path to current screenshot
        threshold: Confidence threshold for detection
    
    Returns:
        True if button was found and tapped, False otherwise
    """
    coords = detect_button_on_screen(button_folder, screenshot_path, threshold)
    if coords:
        x, y = coords
        human_tap(x, y, RANDOM_OFFSET_HEROES)
        return True
    else:
        print(f"No button found in ui form folder: {button_folder}, continuing...")
        return False

def deploy_troop_at_locations(troop_button_folder, deployment_locations, deployment_units, screenshot_path="screen.png"):
    """
    Deploys a specific troop type at multiple locations.
    
    Features:
    - Clicks the troop button to select it
    - Deploys specified number of units
    - Repeats coordinates if more units than locations
    - Shuffles coordinates for randomness
    
    Args:
        troop_button_folder: Folder containing troop button images
        deployment_locations: List of (x, y) coordinates to deploy at
        deployment_units: Number of units to deploy
        screenshot_path: Path to current screenshot
    
    Returns:
        True if troop button was found and deployment started, False otherwise
    """
    if detect_and_tap_button(troop_button_folder, screenshot_path):
        random.shuffle(deployment_locations)
        print(f"Troop button clicked, deploying {deployment_units} units at {len(deployment_locations)} locations")

        # Create a list of coordinates that can accommodate all deployment units
        # If we have more units than locations, repeat the locations
        deployment_coords = []
        for i in range(deployment_units):
            coord_index = i % len(deployment_locations)
            deployment_coords.append(deployment_locations[coord_index])
        
        # Shuffle the final deployment coordinates for randomness
        random.shuffle(deployment_coords)
        
        for i, (x, y) in enumerate(deployment_coords):
            print(f"Deploying unit {i+1}/{deployment_units} at location: ({x}, {y})")
            human_tap(x, y, RANDOM_OFFSET)
            time.sleep(random.uniform(0.3, 0.5))
        return True
    else:
        print(f"Troop not found in image form folder: {troop_button_folder}")
        return False

def deploy_spells_at_locations(troop_button_folder, deployment_locations, screenshot_path="screen.png"):
    """
    Deploys spells at specified locations.
    Uses larger random offset for area coverage.
    
    Args:
        troop_button_folder: Folder containing spell button images
        deployment_locations: List of (x, y) coordinates to deploy at
        screenshot_path: Path to current screenshot
    
    Returns:
        True if spell button was found and deployment started, False otherwise
    """
    if detect_and_tap_button(troop_button_folder, screenshot_path):
        random.shuffle(deployment_locations)
        print(f"Spell button clicked, deploying at {len(deployment_locations)} locations")
        for i, (x, y) in enumerate(deployment_locations):
            human_tap(x, y, RANDOM_OFFSET_SPELLS)
            time.sleep(random.uniform(0.3, 0.5))
        return True
    else:
        print(f"Spell not found in image form folder: {troop_button_folder}")
        return False

def deploy_all_heroes(hero_folder_root, hero_locations, screenshot_path="screen.png"):
    """
    Deploys all available heroes at random locations.
    
    Features:
    - Automatically finds all hero folders
    - Shuffles both heroes and locations for randomness
    - Uses precise tapping for heroes
    
    Args:
        hero_folder_root: Root folder containing hero subfolders
        hero_locations: List of (x, y) coordinates for hero deployment
        screenshot_path: Path to current screenshot
    """
    hero_folders = [os.path.join(hero_folder_root, name) for name in os.listdir(hero_folder_root)
                    if os.path.isdir(os.path.join(hero_folder_root, name))] 
    print(f"Detected hero folders: {hero_folders}") 
    random.shuffle(hero_folders)
    shuffled_locations = hero_locations[:]
    random.shuffle(shuffled_locations)
    for folder, loc in zip(hero_folders, shuffled_locations):
        if detect_and_tap_button_precise(folder, screenshot_path):
            time.sleep(random.uniform(0.3, 0.7))
            human_tap(loc[0], loc[1], RANDOM_OFFSET_HEROES)
            time.sleep(random.uniform(0.5, 1.5))
        else:
            print(f"Hero not found in image from folder: {folder}")

def human_swipe(start_x=300, start_y=300, end_x=300, end_y=600, offset=15, min_duration=200, max_duration=400):
    """
    Simulates human-like swiping with random variations.
    
    Args:
        start_x, start_y: Starting coordinates
        end_x, end_y: Ending coordinates
        offset: Random offset for coordinates
        min_duration, max_duration: Swipe duration range in milliseconds
    """
    sx = start_x + random.randint(-offset, offset)
    sy = start_y + random.randint(-offset, offset)
    ex = end_x + random.randint(-offset, offset)
    ey = end_y + random.randint(-offset, offset)
    duration = random.randint(min_duration, max_duration)
    adb_command = [
        "adb", "shell", "input", "swipe",
        str(sx), str(sy), str(ex), str(ey), str(duration)
    ]
    try:
        subprocess.run(adb_command, check=True)
        print(f"Swiped from ({sx}, {sy}) to ({ex}, {ey}) in {duration} ms.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute swipe: {e}")

# =============================================================================
# MAIN BOT LOOP
# =============================================================================

if __name__ == "__main__":
    loop_count = 0
    while True:
        try:
            loop_count += 1
            print(f"\n=== Starting Main Base Loop {loop_count} ===")
            # Step 0: Get device info
            if selected_device is None:
                selected_device = select_devices()
            
            # Step 1: Collect resources from base
            take_screenshot("screen.png")
            detect_and_tap_button("ui_main_base/gold_collect", "screen.png")
            detect_and_tap_button("ui_main_base/elixir_collect", "screen.png")
            detect_and_tap_button("ui_main_base/dark_elixir_collect", "screen.png")                                  
            
            # Step 2: Find and click attack button
            while True:
                take_screenshot("screen.png")
                if detect_button_on_screen("ui_main_base/attack_button", "screen.png"):
                    print("Attack button detected!")
                    break
                print("Attack button image not detected yet. Waiting...")
                time.sleep(2)
            detect_and_tap_button("ui_main_base/attack_button", "screen.png")
            time.sleep(random.uniform(0.2, 0.5))
            
            # Step 3: Find and click find match button
            while True:
                take_screenshot("screen.png")
                if detect_button_on_screen("ui_main_base/find_match_button", "screen.png"):
                    print("Find match button detected!")
                    break
                detect_and_tap_button("ui_main_base/attack_button", "screen.png")
                time.sleep(2)
            detect_and_tap_button("ui_main_base/find_match_button", "screen.png")
            time.sleep(2)
            
            # Step 4: Find suitable base (meets resource thresholds)
            take_screenshot("screen.png")
            attempt = 1
            while True:
                resources = get_resource_values("screen.png")
                print(f"Attempt {attempt}: Detected resources: {resources}")
                gold = resources.get('gold')
                elixir = resources.get('elixir')
                dark = resources.get('dark_elixir')
                trophies = resources.get('trophies')
                
                # Check if base meets our criteria
                if gold >= gold_threshold and elixir >= elixir_threshold and dark >= dark_elixir_threshold:
                    print("Resource thresholds met. Proceeding with attack.")
                    print("Checking trophies...")
                    if trophies != 0 and trophies <= max_trophies_attack_threshold:
                        print("Trophies also good")  
                        break
                print("Threshold not met. Clicking next battle...")
                detect_and_tap_button("ui_main_base/next_button", "screen.png")      
                time.sleep(random.uniform(4.5, 5))
                take_screenshot("screen.png")
                attempt += 1

            # Step 5: Deploy troops
            # =============================================================================
            # TROOP DEPLOYMENT SECTION - CUSTOMIZE YOUR ARMY COMPOSITION
            # =============================================================================
            # Uncomment and modify the lines below to deploy your preferred troops
            # Format: deploy_troop_at_locations("troop_folder", troop_locations, number_of_units)
            
            # deploy_troop_at_locations("ui_main_base/troops/super_minion", troop_locations, 20)
            # deploy_troop_at_locations("ui_main_base/troops/super_minion", troop_locations, 25)
            deploy_troop_at_locations("ui_main_base/troops/valkyrie", troop_locations, 25)
            #deploy_troop_at_locations("ui_main_base/troops/dragon", troop_locations, 12)
            #deploy_troop_at_locations("ui_main_base/troops/ballon", troop_locations, 12)

            time.sleep(random.uniform(6,7))
            
            # Step 6: Deploy spells (optional)
            # =============================================================================
            # SPELL DEPLOYMENT SECTION - CUSTOMIZE YOUR SPELLS
            # =============================================================================
            # Uncomment and modify the lines below to deploy spells
            # deploy_spells_at_locations("ui_main_base/spells/heal", spell_locations)
            # time.sleep(random.uniform(0.2, 0.5))
            # deploy_spells_at_locations("ui_main_base/spells/ice_spell", ice_spell_locations)
            # time.sleep(random.uniform(0.2, 0.5))
            
            # Step 7: Deploy heroes
            deploy_all_heroes("ui_main_base/hero", hero_locations)

            # Step 8: Deploy additional spells
            deploy_spells_at_locations("ui_main_base/spells/rage", spell_locations)
            time.sleep(random.uniform(6, 8))
            
            # Step 9: Activate hero abilities
            detect_and_tap_button("ui_main_base/hero/grand_warden","screen.png")
            detect_and_tap_button("ui_main_base/hero/minion_prince","screen.png")
            
            # Step 10: Wait for battle to end and return home
            print("Waiting for return home button to appear...")
            while True:
                take_screenshot("screen.png")
                if detect_button_on_screen("ui_main_base/return_home", "screen.png"):
                    print("Return home button detected!")
                    break
                print("Return home button image not detected yet. Waiting...")
                time.sleep(random.uniform(3,3.5))
            detect_and_tap_button("ui_main_base/return_home", "screen.png")
            time.sleep(random.uniform(4, 4.5))
            take_screenshot("screen.png")
            detect_and_tap_button("ui_main_base/okay_button", "screen.png")
            
        except Exception as e:
            print(f"Error in main base loop: {e}")
            time.sleep(2) 
