#!/usr/bin/env python3
"""Control Tab - Start/Stop, Flow, Logs, Stats."""
import tkinter as tk
from tkinter import ttk


class ControlTab:
    """Control tab with device selection, start/stop, flow checkboxes, stats, and logs."""

    def __init__(self, notebook: ttk.Notebook, main_gui):
        self.main = main_gui
        self.frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(self.frame, text="  Control  ")
        self._build()

    def _build(self):
        left_frame = ttk.Frame(self.frame, style="Dark.TFrame", width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Device Section
        ttk.Label(left_frame, text="DEVICE", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        self.main.device_combo = ttk.Combobox(
            left_frame, values=self.main._get_devices(), state="readonly", width=28
        )
        self.main.device_combo.current(0)
        self.main.device_combo.pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(left_frame, text="Refresh", command=self.main._refresh_devices).pack(anchor=tk.W, pady=(0, 10))

        # Webhook Section
        ttk.Label(left_frame, text="WEBHOOK", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))
        self.main.webhook_entry = ttk.Entry(left_frame, width=30)
        self.main.webhook_entry.insert(0, self.main.deploy_config.get("webhook_url", ""))
        self.main.webhook_entry.pack(anchor=tk.W, pady=(0, 10))

        # Start/Stop Button
        self.main.toggle_button = ttk.Button(
            left_frame, text="START BOT", style="Start.TButton", command=self.main._toggle_bot
        )
        self.main.toggle_button.pack(pady=(15, 15), fill=tk.X)

        # Flow Control Section
        ttk.Label(left_frame, text="FLOW CONTROL", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))
        flow_frame = ttk.Frame(left_frame, style="Dark.TFrame")
        flow_frame.pack(anchor=tk.W, fill=tk.X)

        for name, enabled in self.main.flow_state.items():
            var = tk.BooleanVar(value=enabled)
            self.main.flow_vars[name] = var
            ttk.Checkbutton(
                flow_frame, text=f"  {name.replace('_', ' ').title()}", variable=var
            ).pack(anchor=tk.W, pady=2)

        # Right frame - Status & Logs
        right_frame = ttk.Frame(self.frame, style="Dark.TFrame")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Status Section
        ttk.Label(right_frame, text="STATUS", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        self.main.status_label = ttk.Label(
            right_frame, text="● STOPPED", foreground="gray", style="Status.TLabel"
        )
        self.main.status_label.pack(anchor=tk.W, pady=(0, 10))

        # Stats Section
        ttk.Label(right_frame, text="SESSION STATS", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))
        stats_frame = ttk.LabelFrame(right_frame, text="", padding=10)
        stats_frame.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        grid = ttk.Frame(stats_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Runtime:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.main.runtime_label = ttk.Label(grid, text="00:00:00")
        self.main.runtime_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(grid, text="Loop:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.main.loop_label = ttk.Label(grid, text="0")
        self.main.loop_label.grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(grid, text="Gold:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.main.gold_label = ttk.Label(grid, text="0")
        self.main.gold_label.grid(row=2, column=1, sticky=tk.W)

        ttk.Label(grid, text="Elixir:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.main.elixir_label = ttk.Label(grid, text="0")
        self.main.elixir_label.grid(row=3, column=1, sticky=tk.W, pady=5)

        ttk.Label(grid, text="Dark:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.main.dark_label = ttk.Label(grid, text="0")
        self.main.dark_label.grid(row=4, column=1, sticky=tk.W)

        # Log Output Section
        ttk.Label(right_frame, text="LOG OUTPUT", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))

        log_frame = ttk.Frame(right_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.main.log_text = tk.Text(
            log_frame, wrap=tk.WORD, font=("Consolas", 9),
            bg="#1e1e1e", fg="#00ff00", insertbackground="#00ff00",
            relief=tk.FLAT, state=tk.DISABLED, yscrollcommand=log_scroll.set
        )
        self.main.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.main.log_text.yview)

        self.main.log_text.tag_config("INFO", foreground="#00ff00")
        self.main.log_text.tag_config("WARN", foreground="#ffff00")
        self.main.log_text.tag_config("ERROR", foreground="#ff4444")
