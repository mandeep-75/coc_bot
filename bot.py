import time
import random
import config
from utils import notifier
from utils.text_detect_resource import get_resource_values
from utils.wall_upgrade import WallUpgradeManager

class CoCBot:
    def __init__(self, device_controller, webhook_url=None):
        self.device = device_controller
        self.webhook_url = webhook_url
        
        self.loop_count = 0
        self.start_time = time.time()
        
        # Session stats
        self.session_gold = 0
        self.session_elixir = 0
        self.session_dark = 0
        self.last_resources = None

        # Components
        self.wall_manager = WallUpgradeManager(
            builder_menu_button_folder=config.BUILD_MENU_BUTTON_FOLDER,
            screenshot_name=config.SCREENSHOT_NAME,
            random_offset=config.RANDOM_OFFSET,
            okay_button_folder="ui_main_base/okay_button",
            gem_icon_folder="ui_main_base/gem_icon_folder",
            close_button_folder="ui_main_base/close_button_folder",
        )
        
        # Hero positions state
        self.deployed_heroes = {}

    def run(self):
        """Main Bot Loop"""
        notifier.send_session_start(self.webhook_url)
        
        with open(config.LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n\n===== NEW BOT SESSION STARTED =====\n")
            f.write(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        while True:
            try:
                self.loop_count += 1
                print(f"\n=== MAIN LOOP {self.loop_count} START ===")

                self.collect_resources()
                self.upgrade_walls()
                
                # Attack sequence
                if self.find_match():
                    if self.search_for_base():
                        self.perform_attack()
                        self.return_home()
                
                self.log_summary()

            except Exception as e:
                print(f"⚠️ Error in loop: {e}")
                time.sleep(5)

    def collect_resources(self):
        print("Collecting resources...")
        self.device.take_screenshot()
        self.device.detect_and_tap("ui_main_base/gold_collect")
        self.device.detect_and_tap("ui_main_base/elixir_collect")
        self.device.detect_and_tap("ui_main_base/dark_elixir_collect")

    def upgrade_walls(self):
        if not config.WALL_UPGRADES_ENABLED:
            return

        # Hooks adapter for the existing WallUpgradeManager
        # It expects specific function signatures
        hooks = {
            'device_id': self.device.device_id,
            'take_screenshot': lambda: self.device.take_screenshot(config.SCREENSHOT_NAME),
            'detect_and_tap_button': lambda folder: self.device.detect_and_tap(folder),
            'human_tap': lambda x, y, offset: self.device.tap(x, y, offset),
            'detect_button': lambda folder: self.device.detect_button(folder),
        }
        self.wall_manager.maybe_upgrade_walls(self.loop_count, hooks)

    def find_match(self):
        """Navigates to the attack screen and clicks Find Match."""
        start_wait = time.time()
        
        # 1. Click Attack Button
        while True:
            if time.time() - start_wait > 30:
                print("⏭️ Timeout waiting for initial Attack button.")
                return False
            
            self.device.take_screenshot()
            if self.device.detect_and_tap("ui_main_base/attack_button"):
                print("Attack button tapped.")
                break
            time.sleep(2)
        
        time.sleep(1) # Animation wait

        # 2. Click Find Match
        start_wait = time.time()
        while True:
            if time.time() - start_wait > 30:
                print("⏭️ Timeout waiting for Find Match button.")
                return False
                
            self.device.take_screenshot()
            if self.device.detect_and_tap("ui_main_base/find_match_button"):
                print("Find Match button tapped.")
                break
           
            
            # Handle accidental screens (like okay button)
            self.device.detect_and_tap("ui_main_base/okay_button")
            # Retry attack button if we somehow got kicked out
            if self.device.detect_and_tap("ui_main_base/attack_button"):
                print("Retrying attack button...")
        while True: 
            time.sleep(2)
            self.device.take_screenshot()    
            if self.device.detect_and_tap("ui_main_base/attack_button"):
                print("Attack button tapped.")
                return True         

    def search_for_base(self):
        """Searches for a base meeting resource requirements."""
        self.device.take_screenshot()
        attempt = 1
        search_start = time.time()
        
        while True:
            if time.time() - search_start > 120:
                print("⏭️ Timeout searching for base.")
                return False

            resources = get_resource_values(config.SCREENSHOT_NAME)
            gold = resources.get('gold', 0)
            elixir = resources.get('elixir', 0)
            dark = resources.get('dark_elixir', 0)

            # Check duplication/ocr errors
            if self.last_resources == resources or (gold == 0 and elixir == 0 and dark == 0):
                print(f"Base {attempt}: (skipping invalid/duplicate read)")
            else:
                print(f"Base {attempt}: Gold={gold:,} Elixir={elixir:,} Dark={dark:,}")

            self.last_resources = resources.copy()

            if (gold >= config.GOLD_THRESHOLD or elixir >= config.ELIXIR_THRESHOLD) and dark >= config.DARK_ELIXIR_THRESHOLD:
                print("✅ Target found! Launching attack.")
                self.session_gold += gold
                self.session_elixir += elixir
                self.session_dark += dark
                
                # Log attack
                with open(config.LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"Attack {self.loop_count}: Gold={gold:,}, Elixir={elixir:,}, Dark={dark:,}\n")
                
                notifier.send_attack_summary(self.webhook_url, self.loop_count, gold, elixir, dark)
                return True

            # Next Base
            print("❌ Skipping...")
            if self.device.detect_and_tap("ui_main_base/next_button"):
                search_start = time.time() # Reset timeout on successful next
            else:
                print("⚠️ Next button not found?")
            
            time.sleep(random.uniform(4.5, 5)) # Wait for cloud animation
            self.device.take_screenshot()
            attempt += 1

    def perform_attack(self):
        """Deploys troops, heroes, and spells."""
        # 1. Deploy Troops
        if self.device.detect_and_tap("ui_main_base/troops/super_minion"):
            print("Deploying super minions...")
            
            # Group locations in batches to simulate fingers or waves if needed
            # For now, just iterate
            # Shuffle troop locations for variety
            locs = config.TROOP_LOCATIONS[:]
            random.shuffle(locs)
            
            # Deploy 24 units as per original code
            units_to_deploy = 24
            for i in range(units_to_deploy):
                tgt = locs[i % len(locs)]
                self.device.tap(tgt[0], tgt[1], config.RANDOM_OFFSET)
                time.sleep(random.uniform(0.1, 0.2))
        else:
            print("⚠️ Troop button not found!")

        time.sleep(random.uniform(4, 5))

        # 2. Deploy Heroes
        self.deployed_heroes = {} # Reset
        # Get hero folders (assume they are in ui_main_base/hero)
        # We need to iterate over folders in ui_main_base/hero
        # Since we can't easily glob from inside the class without importing glob/os, 
        # let's assume specific heroes or dynamic check.
        # Original code did dynamic walk. Let's do that cleanly.
        import os
        hero_root = "ui_main_base/hero"
        if os.path.isdir(hero_root):
            hero_folders = [os.path.join(hero_root, f) for f in os.listdir(hero_root) if os.path.isdir(os.path.join(hero_root, f))]
            random.shuffle(hero_folders)
            
            hero_locs = config.HERO_LOCATIONS[:]
            random.shuffle(hero_locs)
            
            for folder, loc in zip(hero_folders, hero_locs):
                hero_name = os.path.basename(folder)
                coords = self.device.detect_button(folder, threshold=0.8) # Precise check first
                if coords:
                    print(f"Deploying {hero_name}")
                    # Tap the hero card
                    self.device.tap(coords[0], coords[1], config.RANDOM_OFFSET_HEROES)
                    time.sleep(0.2)
                    # Tap the field
                    self.device.tap(loc[0], loc[1], config.RANDOM_OFFSET_HEROES)
                    # Store for ability
                    self.deployed_heroes[hero_name] = coords
                    time.sleep(random.uniform(0.5, 1.0))
        
        # 3. Deploy Spells
        if self.device.detect_and_tap("ui_main_base/spells/rage"):
            print("Deploying spells...")
            for loc in config.SPELL_LOCATIONS:
                self.device.tap(loc[0], loc[1], config.RANDOM_OFFSET_SPELLS)
                time.sleep(0.3)
        
        time.sleep(random.uniform(5, 8))
        
        # 4. Trigger Warden Ability (example)
        self.trigger_hero_ability("grand_warden")

    def trigger_hero_ability(self, hero_name_partial):
        # Look for the hero in our deployed list
        for name, coords in self.deployed_heroes.items():
            if hero_name_partial in name.lower():
                print(f"✨ Activating {name} ability!")
                self.device.tap(coords[0], coords[1], config.RANDOM_OFFSET_HEROES)
                break

    def return_home(self):
        print("Waiting for battle end (Return Home)...")
        wait_start = time.time()
        
        while True:
            if time.time() - wait_start > 210: # 3.5 mins
                print("Force ending battle.")
                break # Proceed to force quit check
            
            self.device.take_screenshot()
            
            if self.device.detect_and_tap("ui_main_base/return_home"):
                print("Returning home...")
                time.sleep(3)
                self.device.detect_and_tap("ui_main_base/okay_button")
                return

            if time.time() - wait_start > 20 and random.random() < 0.05:
                # Randomly check for surrender if taking too long or just to end early?
                # The original code had a surrender logic that was a bit complex/buggy looking in the loop.
                # I'll implement a simple "End Battle" check if it exists
                pass

            time.sleep(3)
        
        # Force quit logic if timeout or needed
        self.device.take_screenshot()
        self.device.detect_and_tap("ui_main_base/end_battle")
        self.device.detect_and_tap("ui_main_base/surrender_button")
        time.sleep(1)
        self.device.take_screenshot()
        self.device.detect_and_tap("ui_main_base/return_home")

    def log_summary(self):
        if self.loop_count % 5 == 0:
            elapsed_min = (time.time() - self.start_time) / 60
            avg_gold = self.session_gold / self.loop_count
            avg_elixir = self.session_elixir / self.loop_count
            avg_dark = self.session_dark / self.loop_count
            
            summary = (
                f"\n===== SESSION SUMMARY =====\n"
                f"Attacks: {self.loop_count}\n"
                f"Avg Gold: {avg_gold:,.0f}\n"
                f"Avg Elixir: {avg_elixir:,.0f}\n"
                f"Avg Dark: {avg_dark:,.0f}\n"
                f"Runtime: {elapsed_min:.1f} min\n"
                f"===========================\n"
            )
            print(summary)
            with open(config.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(summary)
