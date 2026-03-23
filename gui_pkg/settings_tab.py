#!/usr/bin/env python3
"""Settings Tab - Deployment, Troops, Spells, Heroes, Thresholds, Timeouts."""
import tkinter as tk
from tkinter import ttk, messagebox


class SettingsTab:
    """Settings tab with all configuration options."""

    def __init__(self, notebook: ttk.Notebook, main_gui):
        self.main = main_gui
        self.frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(self.frame, text="  Settings  ")
        self._build()

    def _build(self):
        # Left column - Deployment & Troops & Spells & Heroes
        left_col = ttk.Frame(self.frame, style="Dark.TFrame")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Deployment Section
        deploy_section = ttk.LabelFrame(left_col, text="DEPLOYMENT OFFSETS", padding=10)
        deploy_section.pack(fill=tk.X, pady=(0, 10))

        offset_configs = [
            ("random_offset_troops", "Troop Offset:", 0, 20),
            ("random_offset_heroes", "Hero Offset:", 0, 20),
            ("random_offset_spells", "Spell Offset:", 0, 50),
        ]

        for key, label, min_val, max_val in offset_configs:
            ttk.Label(deploy_section, text=label).pack(anchor=tk.W, pady=(5, 0))
            var = tk.IntVar(value=self.main.deploy_config.get(key, 3))
            self.main.settings_entries[key] = var
            slider = ttk.Scale(
                deploy_section, from_=min_val, to=max_val, variable=var, orient=tk.HORIZONTAL
            )
            slider.pack(fill=tk.X)
            ttk.Label(deploy_section, textvariable=var).pack(anchor=tk.W)

        # Troop Selection Section
        self._create_selection_section(
            left_col, "TROOP SELECTION", "troops", 
            self.main.deploy_config.get_troop_folders(),
            self.main.deploy_config.get("selected_troops", []),
            self.main.deploy_config.get("troop_counts", {}),
            "troop_vars", "troop_count_vars"
        )

        # Spell Selection Section
        self._create_selection_section(
            left_col, "SPELL SELECTION", "spells",
            self.main.deploy_config.get_spell_folders(),
            self.main.deploy_config.get("selected_spells", []),
            self.main.deploy_config.get("spell_counts", {}),
            "spell_vars", "spell_count_vars"
        )

        # Right column - Thresholds & Timeouts
        right_col = ttk.Frame(self.frame, style="Dark.TFrame")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Hero Selection Section (on right side since it's smaller)
        hero_section = ttk.LabelFrame(right_col, text="HERO SELECTION", padding=10)
        hero_section.pack(fill=tk.X, pady=(0, 10))

        hero_scroll = ttk.Scrollbar(hero_section)
        hero_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        hero_list_frame = ttk.Frame(hero_section)
        hero_list_frame.pack(fill=tk.BOTH, expand=True)

        hero_canvas = tk.Canvas(hero_list_frame, bg="#2d2d2d", highlightthickness=0)
        hero_scroll.config(command=hero_canvas.yview)
        hero_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.main.hero_frame_inner = ttk.Frame(hero_canvas)
        hero_canvas.create_window((0, 0), window=self.main.hero_frame_inner, anchor=tk.NW)
        hero_canvas.config(yscrollcommand=hero_scroll.set)

        available_heroes = self.main.deploy_config.get_hero_folders()
        selected_heroes = self.main.deploy_config.get("selected_heroes", [])
        hero_counts = self.main.deploy_config.get("hero_counts", {})

        if not hasattr(self.main, 'hero_count_vars'):
            self.main.hero_count_vars = {}

        for hero in available_heroes:
            row_frame = ttk.Frame(self.main.hero_frame_inner)
            row_frame.pack(fill=tk.X, pady=2)

            var = tk.BooleanVar(value=hero in selected_heroes)
            self.main.hero_vars[hero] = var
            ttk.Checkbutton(
                row_frame, text=f"  {hero.replace('_', ' ').title()}", variable=var
            ).pack(side=tk.LEFT)

            count_var = tk.IntVar(value=hero_counts.get(hero, 1))
            self.main.hero_count_vars[hero] = count_var
            ttk.Label(row_frame, text="Count:").pack(side=tk.LEFT, padx=(10, 2))
            ttk.Entry(row_frame, textvariable=count_var, width=5).pack(side=tk.LEFT)

        self.main.hero_frame_inner.update_idletasks()
        hero_canvas.config(scrollregion=hero_canvas.bbox("all"))

        # Thresholds Section
        threshold_section = ttk.LabelFrame(right_col, text="RESOURCE THRESHOLDS", padding=10)
        threshold_section.pack(fill=tk.X, pady=(0, 10))

        threshold_configs = [
            ("gold_threshold", "Minimum Gold:", 0, 2_000_000, 100_000),
            ("elixir_threshold", "Minimum Elixir:", 0, 2_000_000, 100_000),
            ("dark_threshold", "Minimum Dark Elixir:", 0, 100_000, 1_000),
        ]

        for key, label, min_val, max_val, step in threshold_configs:
            ttk.Label(threshold_section, text=label).pack(anchor=tk.W)
            var = tk.IntVar(value=self.main.deploy_config.get(key, 0))
            self.main.settings_entries[key] = var
            ttk.Entry(threshold_section, textvariable=var, width=15).pack(anchor=tk.W, pady=(0, 5))

        # Timeout Section
        timeout_section = ttk.LabelFrame(right_col, text="TIMEOUTS (seconds)", padding=10)
        timeout_section.pack(fill=tk.X, pady=(0, 10))

        timeout_configs = [
            ("base_search_timeout", "Base Search Timeout:", 30, 300),
            ("return_home_timeout", "Return Home Timeout:", 30, 300),
        ]

        for key, label, min_val, max_val in timeout_configs:
            ttk.Label(timeout_section, text=label).pack(anchor=tk.W)
            var = tk.IntVar(value=self.main.deploy_config.get(key, 120))
            self.main.settings_entries[key] = var
            slider = ttk.Scale(
                timeout_section, from_=min_val, to=max_val, variable=var, orient=tk.HORIZONTAL
            )
            slider.pack(fill=tk.X)
            ttk.Label(timeout_section, textvariable=var).pack(anchor=tk.W)

        # Webhook Section
        webhook_section = ttk.LabelFrame(right_col, text="WEBHOOK", padding=10)
        webhook_section.pack(fill=tk.X, pady=(0, 10))

        webhook_var = tk.StringVar(value=self.main.deploy_config.get("webhook_url", ""))
        self.main.settings_entries["webhook_url"] = webhook_var
        ttk.Entry(webhook_section, textvariable=webhook_var, width=40).pack(fill=tk.X)

        # Save/Reset buttons
        btn_frame = ttk.Frame(right_col)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Save Settings", command=self._save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Reset to Defaults", command=self._reset_settings).pack(side=tk.LEFT)

    def _create_selection_section(self, parent, title, folder_name, items, selected, counts, var_name, count_var_name):
        """Create a selection section with checkboxes and counts."""
        section = ttk.LabelFrame(parent, text=title, padding=10)
        section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scroll = ttk.Scrollbar(section)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        list_frame = ttk.Frame(section)
        list_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(list_frame, bg="#2d2d2d", highlightthickness=0)
        scroll.config(command=canvas.yview)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)
        canvas.config(yscrollcommand=scroll.set)

        # Initialize vars dicts if needed
        if not hasattr(self.main, var_name):
            setattr(self.main, var_name, {})
        if not hasattr(self.main, count_var_name):
            setattr(self.main, count_var_name, {})

        var_dict = getattr(self.main, var_name)
        count_var_dict = getattr(self.main, count_var_name)

        default_count = 14 if folder_name == "troops" else 1

        for item in items:
            row_frame = ttk.Frame(inner_frame)
            row_frame.pack(fill=tk.X, pady=2)

            var = tk.BooleanVar(value=item in selected)
            var_dict[item] = var
            ttk.Checkbutton(
                row_frame, text=f"  {item.replace('_', ' ').title()}", variable=var
            ).pack(side=tk.LEFT)

            count_var = tk.IntVar(value=counts.get(item, default_count))
            count_var_dict[item] = count_var
            ttk.Label(row_frame, text="Count:").pack(side=tk.LEFT, padx=(10, 2))
            ttk.Entry(row_frame, textvariable=count_var, width=5).pack(side=tk.LEFT)

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def _save_settings(self):
        self.save_settings_to_config()
        self.main.log_capture.info("Settings saved successfully!")
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def save_settings_to_config(self):
        # Save simple settings
        for key, var in self.main.settings_entries.items():
            try:
                self.main.deploy_config.set(key, var.get())
            except tk.TclError:
                pass

        # Save troop selection & counts
        selected = [t for t, var in self.main.troop_vars.items() if var.get()]
        self.main.deploy_config.set("selected_troops", selected)

        if hasattr(self.main, 'troop_count_vars'):
            counts = {}
            for t, var in self.main.troop_count_vars.items():
                try:
                    c = var.get()
                    if c > 0:
                        counts[t] = c
                except tk.TclError:
                    pass
            self.main.deploy_config.set("troop_counts", counts)

        # Save spell selection & counts
        if hasattr(self.main, 'spell_vars'):
            selected_spells = [s for s, var in self.main.spell_vars.items() if var.get()]
            self.main.deploy_config.set("selected_spells", selected_spells)

        if hasattr(self.main, 'spell_count_vars'):
            spell_counts = {}
            for s, var in self.main.spell_count_vars.items():
                try:
                    c = var.get()
                    if c > 0:
                        spell_counts[s] = c
                except tk.TclError:
                    pass
            self.main.deploy_config.set("spell_counts", spell_counts)

        # Save hero selection & counts
        if hasattr(self.main, 'hero_vars'):
            selected_heroes = [h for h, var in self.main.hero_vars.items() if var.get()]
            self.main.deploy_config.set("selected_heroes", selected_heroes)

        if hasattr(self.main, 'hero_count_vars'):
            hero_counts = {}
            for h, var in self.main.hero_count_vars.items():
                try:
                    c = var.get()
                    if c > 0:
                        hero_counts[h] = c
                except tk.TclError:
                    pass
            self.main.deploy_config.set("hero_counts", hero_counts)

    def _reset_settings(self):
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.main.deploy_config.reset_to_defaults()
            self.main.log_capture.warning("Settings reset to defaults")
            messagebox.showinfo("Settings", "Settings reset to defaults. Please restart the GUI.")