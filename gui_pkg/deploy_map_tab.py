#!/usr/bin/env python3
"""Deployment Map Tab - Screenshot with dots, location editor."""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

import config


class DeployMapTab:
    """Deployment map tab with screenshot and location editor."""

    CANVAS_DEFAULT_WIDTH = 400
    CANVAS_DEFAULT_HEIGHT = 600

    def __init__(self, notebook: ttk.Notebook, main_gui):
        self.main = main_gui
        self.frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(self.frame, text="  Deployment Map  ")
        self.screenshot_canvas = None
        self.location_table = None
        self.loc_type_var = None
        self.edit_x = None
        self.edit_y = None
        self.add_coords = None
        self.img_scale = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0
        self._resize_after_id = None
        self._build()

    def _build(self):
        # Top section - Screenshot and Editor side by side
        top_frame = ttk.Frame(self.frame, style="Dark.TFrame")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Screenshot canvas
        canvas_frame = ttk.LabelFrame(top_frame, text="SCREENSHOT MAP", padding=5)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.screenshot_canvas = tk.Canvas(
            canvas_frame, bg="#333333",
            width=self.CANVAS_DEFAULT_WIDTH,
            height=self.CANVAS_DEFAULT_HEIGHT,
            highlightthickness=1
        )
        self.screenshot_canvas.pack(padx=5, pady=5)
        self.screenshot_canvas.bind("<Configure>", self._on_canvas_resize)
        self.screenshot_canvas.bind("<Button-1>", self._on_canvas_click)

        # Legend
        legend_frame = ttk.Frame(canvas_frame)
        legend_frame.pack(fill=tk.X)
        ttk.Label(legend_frame, text="Red = Troops", foreground="#ff4444").pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="Blue = Spells", foreground="#4488ff").pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="Green = Heroes", foreground="#44ff44").pack(side=tk.LEFT, padx=5)

        ttk.Button(canvas_frame, text="Refresh Screenshot", command=self._refresh_screenshot).pack(pady=5)

        # Right side - Location editor
        editor_frame = ttk.LabelFrame(top_frame, text="LOCATION EDITOR", padding=10)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Type selector
        type_frame = ttk.Frame(editor_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.loc_type_var = tk.StringVar(value="troop")
        type_combo = ttk.Combobox(
            type_frame, textvariable=self.loc_type_var,
            values=["troop", "spell", "hero"], state="readonly", width=10
        )
        type_combo.pack(side=tk.LEFT)
        type_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_location_table())
        ttk.Button(type_frame, text="Refresh", width=3, command=self.refresh_location_table).pack(side=tk.LEFT, padx=5)

        # Location table
        table_frame = ttk.Frame(editor_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("index", "x", "y")
        self.location_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.location_table.heading("index", text="#")
        self.location_table.heading("x", text="X")
        self.location_table.heading("y", text="Y")
        self.location_table.column("index", width=40)
        self.location_table.column("x", width=80)
        self.location_table.column("y", width=80)

        table_scroll = ttk.Scrollbar(table_frame, command=self.location_table.yview)
        self.location_table.configure(yscrollcommand=table_scroll.set)

        self.location_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.location_table.bind("<<TreeviewSelect>>", self._on_location_select)

        # Edit fields
        edit_frame = ttk.Frame(editor_frame)
        edit_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(edit_frame, text="X:").pack(side=tk.LEFT)
        self.edit_x = ttk.Entry(edit_frame, width=8)
        self.edit_x.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(edit_frame, text="Y:").pack(side=tk.LEFT)
        self.edit_y = ttk.Entry(edit_frame, width=8)
        self.edit_y.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(edit_frame, text="Update", command=self._update_selected_location).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(edit_frame, text="Delete", command=self._delete_selected_location).pack(side=tk.LEFT)

        # Bottom buttons
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(bottom_frame, text="Add new point:").pack(side=tk.LEFT, padx=(0, 10))
        add_x = ttk.Entry(bottom_frame, width=8)
        add_x.pack(side=tk.LEFT)
        ttk.Label(bottom_frame, text=",").pack(side=tk.LEFT)
        add_y = ttk.Entry(bottom_frame, width=8)
        add_y.pack(side=tk.LEFT, padx=(0, 5))
        self.add_coords = (add_x, add_y)

        ttk.Button(bottom_frame, text="+ Troop", command=lambda: self._add_location("troop")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(bottom_frame, text="+ Spell", command=lambda: self._add_location("spell")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(bottom_frame, text="+ Hero", command=lambda: self._add_location("hero")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(bottom_frame, text="Reset All", command=self._reset_locations).pack(side=tk.RIGHT)

    def _on_canvas_resize(self, event):
        if self._resize_after_id:
            self.main.window.after_cancel(self._resize_after_id)
        self._resize_after_id = self.main.window.after(100, self._draw_deployment_dots)

    def _on_canvas_click(self, event):
        x, y = event.x, event.y
        add_x, add_y = self.add_coords
        if add_x and add_y:
            add_x.delete(0, tk.END)
            add_x.insert(0, str(x))
            add_y.delete(0, tk.END)
            add_y.insert(0, str(y))

    def _refresh_screenshot(self):
        try:
            device_id = self.main.device_combo.get() if self.main.device_combo else None
            if device_id and device_id not in ["No devices", "ADB Error", ""]:
                subprocess.run(
                    ["adb", "-s", device_id, "exec-out", "screencap", "-p"],
                    stdout=open(config.SCREENSHOT_NAME, "wb"),
                    check=True
                )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        self._draw_deployment_dots()

    def refresh_location_table(self):
        if not self.location_table:
            return
        loc_type = self.loc_type_var.get() if self.loc_type_var else "troop"
        key_map = {"troop": "troop_locations", "spell": "spell_locations", "hero": "hero_locations"}
        key = key_map.get(loc_type, "troop_locations")
        locations = self.main.deploy_config.get(key, [])
        try:
            for item in self.location_table.get_children():
                self.location_table.delete(item)
            for i, (x, y) in enumerate(locations):
                self.location_table.insert("", tk.END, values=(i + 1, x, y))
        except tk.TclError:
            return
        self._draw_deployment_dots()

    def delayed_screenshot_init(self):
        self.refresh_location_table()
        self._refresh_screenshot()

    def _on_location_select(self, event):
        selection = self.location_table.selection()
        if selection:
            item = self.location_table.item(selection[0])
            idx, x, y = item["values"]
            self.main.selected_loc_index = idx - 1
            self.main.selected_loc_type = self.loc_type_var.get()
            self.edit_x.delete(0, tk.END)
            self.edit_x.insert(0, str(x))
            self.edit_y.delete(0, tk.END)
            self.edit_y.insert(0, str(y))

    def _update_selected_location(self):
        if self.main.selected_loc_index is None:
            messagebox.showwarning("No Selection", "Select a location first")
            return
        try:
            x, y = int(self.edit_x.get()), int(self.edit_y.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Enter valid numbers")
            return
        self.main.deploy_config.update_location(
            self.main.selected_loc_type, self.main.selected_loc_index, x, y
        )
        self.refresh_location_table()
        self.main.log_capture.info(f"Updated {self.main.selected_loc_type} location")

    def _delete_selected_location(self):
        if self.main.selected_loc_index is None:
            messagebox.showwarning("No Selection", "Select a location first")
            return
        self.main.deploy_config.remove_location(
            self.main.selected_loc_type, self.main.selected_loc_index
        )
        self.refresh_location_table()
        self.main.selected_loc_index = None
        self.edit_x.delete(0, tk.END)
        self.edit_y.delete(0, tk.END)
        self.main.log_capture.info(f"Deleted {self.main.selected_loc_type} location")

    def _add_location(self, loc_type: str):
        add_x, add_y = self.add_coords
        try:
            x, y = int(add_x.get()), int(add_y.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Enter valid coordinates")
            return
        self.main.deploy_config.add_location(loc_type, x, y)
        if self.loc_type_var.get() != loc_type:
            self.loc_type_var.set(loc_type)
        self.refresh_location_table()
        self.main.log_capture.info(f"Added {loc_type} location")
        add_x.delete(0, tk.END)
        add_y.delete(0, tk.END)

    def _reset_locations(self):
        if messagebox.askyesno("Reset Locations", "Reset all deployment locations to defaults?"):
            self.main.deploy_config.set("troop_locations", config.TROOP_LOCATIONS)
            self.main.deploy_config.set("spell_locations", config.SPELL_LOCATIONS)
            self.main.deploy_config.set("hero_locations", config.HERO_LOCATIONS)
            self.refresh_location_table()
            self.main.log_capture.warning("Deployment locations reset to defaults")

    def _draw_deployment_dots(self):
        if not self.screenshot_canvas:
            return
        try:
            if not self.screenshot_canvas.winfo_exists():
                return
        except tk.TclError:
            return

        try:
            self.screenshot_canvas.delete("all")
        except tk.TclError:
            return

        self.img_scale = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0

        if os.path.exists(config.SCREENSHOT_NAME):
            try:
                from PIL import Image, ImageTk
                img = Image.open(config.SCREENSHOT_NAME)
                img_w, img_h = img.size
                if img_w <= 0 or img_h <= 0:
                    raise ValueError("Invalid image")
                canvas_w = self.screenshot_canvas.winfo_width()
                canvas_h = self.screenshot_canvas.winfo_height()
                if canvas_w <= 0:
                    canvas_w = self.CANVAS_DEFAULT_WIDTH
                if canvas_h <= 0:
                    canvas_h = self.CANVAS_DEFAULT_HEIGHT
                scale = min(canvas_w / img_w, canvas_h / img_h)
                if scale <= 0:
                    scale = 1.0
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                if new_w <= 0 or new_h <= 0:
                    new_w, new_h = img_w, img_h
                    scale = 1.0
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                self.main.screenshot_image = ImageTk.PhotoImage(img)
                self.img_offset_x = (canvas_w - new_w) // 2
                self.img_offset_y = (canvas_h - new_h) // 2
                self.screenshot_canvas.create_image(
                    self.img_offset_x, self.img_offset_y, anchor=tk.NW, image=self.main.screenshot_image
                )
                self.img_scale = scale
            except Exception:
                self.screenshot_canvas.create_text(200, 300, text="Screenshot unavailable", fill="white")
        else:
            self.screenshot_canvas.create_text(200, 300, text="No screenshot - click Refresh with device", fill="gray")

        # Draw dots
        self._draw_dots("troop_locations", "#ff4444", self.main.deploy_config.get("troop_locations", []))
        self._draw_dots("spell_locations", "#4488ff", self.main.deploy_config.get("spell_locations", []))
        self._draw_dots("hero_locations", "#44ff44", self.main.deploy_config.get("hero_locations", []))

    def _draw_dots(self, key: str, color: str, locations: list):
        for x, y in locations:
            sx = x * self.img_scale + self.img_offset_x
            sy = y * self.img_scale + self.img_offset_y
            try:
                self.screenshot_canvas.create_oval(
                    sx - 4, sy - 4, sx + 4, sy + 4,
                    fill=color, outline=color
                )
            except tk.TclError:
                pass
