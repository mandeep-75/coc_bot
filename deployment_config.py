#!/usr/bin/env python3
"""
Deployment Configuration Manager
Handles loading/saving deployment settings to JSON with fallback to config.py defaults.
"""
import json
import os
from typing import Any

import config


class DeploymentConfig:
    """Manages deployment settings with JSON persistence."""
    
    DEFAULTS = {
        "troop_counts": {},
        "spell_counts": {},
        "hero_counts": {},
        "random_offset_troops": config.RANDOM_OFFSET,
        "random_offset_heroes": config.RANDOM_OFFSET_HEROES,
        "random_offset_spells": config.RANDOM_OFFSET_SPELLS,
        "gold_threshold": config.GOLD_THRESHOLD,
        "elixir_threshold": config.ELIXIR_THRESHOLD,
        "dark_threshold": config.DARK_ELIXIR_THRESHOLD,
        "base_search_timeout": config.BASE_SEARCH_TIMEOUT,
        "return_home_timeout": config.RETURN_HOME_TIMEOUT,
        "troop_locations": config.TROOP_LOCATIONS,
        "spell_locations": config.SPELL_LOCATIONS,
        "hero_locations": config.HERO_LOCATIONS,
        "selected_troops": ["super_minion"],
        "selected_spells": ["rage"],
        "selected_heroes": [],
        "webhook_url": config.DISCORD_WEBHOOK_URL,
    }
    
    def __init__(self, json_path: str = "deployment_config.json"):
        self.json_path = json_path
        self.config = self._load()
    
    def _load(self) -> dict:
        """Load from JSON, merge with defaults for missing keys."""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                # Merge with defaults (user_config takes precedence)
                merged = self.DEFAULTS.copy()
                merged.update(user_config)
                return merged
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config: {e}, using defaults")
                return self.DEFAULTS.copy()
        return self.DEFAULTS.copy()
    
    def save(self) -> None:
        """Persist current config to JSON."""
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error: Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a config value and save."""
        self.config[key] = value
        self.save()
    
    def get_troop_folders(self) -> list[str]:
        """Scan ui_main_base/troops/ for available troops."""
        troop_root = "ui_main_base/troops"
        if not os.path.isdir(troop_root):
            return []
        folders = [
            f for f in os.listdir(troop_root)
            if os.path.isdir(os.path.join(troop_root, f))
        ]
        return sorted(folders)
    
    def get_spell_folders(self) -> list[str]:
        """Scan ui_main_base/spells/ for available spells."""
        spell_root = "ui_main_base/spells"
        if not os.path.isdir(spell_root):
            return []
        folders = [
            f for f in os.listdir(spell_root)
            if os.path.isdir(os.path.join(spell_root, f))
        ]
        return sorted(folders)
    
    def get_hero_folders(self) -> list[str]:
        """Scan ui_main_base/hero/ for available heroes."""
        hero_root = "ui_main_base/hero"
        if not os.path.isdir(hero_root):
            return []
        folders = [
            f for f in os.listdir(hero_root)
            if os.path.isdir(os.path.join(hero_root, f))
        ]
        return sorted(folders)
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to config.py defaults."""
        self.config = self.DEFAULTS.copy()
        self.save()
    
    def add_location(self, loc_type: str, x: int, y: int) -> None:
        """Add a deployment location."""
        key_map = {
            "troop": "troop_locations",
            "spell": "spell_locations", 
            "hero": "hero_locations",
        }
        key = key_map.get(loc_type.lower())
        if key:
            self.config[key].append((x, y))
            self.save()
    
    def remove_location(self, loc_type: str, index: int) -> None:
        """Remove a deployment location by index."""
        key_map = {
            "troop": "troop_locations",
            "spell": "spell_locations",
            "hero": "hero_locations",
        }
        key = key_map.get(loc_type.lower())
        if key and 0 <= index < len(self.config[key]):
            self.config[key].pop(index)
            self.save()
    
    def update_location(self, loc_type: str, index: int, x: int, y: int) -> None:
        """Update a deployment location."""
        key_map = {
            "troop": "troop_locations",
            "spell": "spell_locations",
            "hero": "hero_locations",
        }
        key = key_map.get(loc_type.lower())
        if key and 0 <= index < len(self.config[key]):
            self.config[key][index] = (x, y)
            self.save()
    
    def set_locations(self, loc_type: str, locations: list[tuple[int, int]]) -> None:
        """Set all locations for a type."""
        key_map = {
            "troop": "troop_locations",
            "spell": "spell_locations",
            "hero": "hero_locations",
        }
        key = key_map.get(loc_type.lower())
        if key:
            self.config[key] = locations
            self.save()
