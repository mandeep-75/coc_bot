#!/usr/bin/env python3
"""Help Tab - Usage instructions and configuration guide."""
import tkinter as tk
from tkinter import ttk


class HelpTab:
    """Help tab with scrollable documentation."""

    def __init__(self, notebook: ttk.Notebook, main_gui):
        self.main = main_gui
        self.frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(self.frame, text="  Help  ")
        self._build()

    def _build(self):
        # Use Text widget with Scrollbar for proper scrolling
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(
            text_frame, wrap=tk.WORD, font=("Consolas", 10),
            bg="#1e1e1e", fg="#cccccc", insertbackground="#cccccc",
            relief=tk.FLAT, yscrollcommand=scrollbar.set,
            state=tk.DISABLED
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)

        # Configure tags for styling
        self.text.tag_configure("title", font=("Consolas", 14, "bold"), foreground="#ffffff")
        self.text.tag_configure("header", font=("Consolas", 11, "bold"), foreground="#00ff00")
        self.text.tag_configure("section", font=("Consolas", 10, "bold"), foreground="#ffff00")
        self.text.tag_configure("indent", lmargin1=20, lmargin2=20)
        self.text.tag_configure("gap", spacing1=10)

        self._add_content()

    def _add_content(self):
        content = [
            ("title", "⚔️ CoC Bot - How to Use & Configure\n\n"),

            ("header", "🚀 QUICK START\n"),
            ("normal", "1. Connect your Android device with ADB\n"),
            ("normal", "2. Select device from dropdown (Control tab)\n"),
            ("normal", "3. Configure troops & settings (Settings tab)\n"),
            ("normal", "4. Click 'START BOT' to begin\n"),
            ("normal", "5. Click 'STOP BOT' to halt (waits for current loop)\n\n"),

            ("header", "📊 CONTROL TAB\n"),
            ("normal", "• DEVICE: Select your Android device\n"),
            ("indent", "  - Click 'Refresh' if device not detected\n"),
            ("normal", "• WEBHOOK: Discord webhook URL for notifications\n"),
            ("normal", "• START BOT: Begins the automation loop\n"),
            ("normal", "• STOP BOT: Stops after current loop completes\n"),
            ("normal", "• FLOW CONTROL: Toggle individual automation tasks\n"),
            ("normal", "• STATUS: Shows current bot state (Running/Stopped)\n"),
            ("normal", "• LOGS: Real-time bot activity log\n"),
            ("normal", "• STATS: Gold/Elixir/Dark collected this session\n\n"),

            ("header", "⚙️ SETTINGS TAB\n"),
            ("section", "DEPLOYMENT:\n"),
            ("normal", "• Troop/Hero/Spell Random Offset:\n"),
            ("indent", "  Click variation (0-20 pixels)\n\n"),

            ("section", "TROOP SELECTION:\n"),
            ("normal", "• ☑ Checkbox: Enable/disable troop type\n"),
            ("normal", "• Count: Number of this troop to deploy\n"),
            ("normal", "• Total = sum of all selected troop counts\n\n"),

            ("section", "THRESHOLDS:\n"),
            ("normal", "• Gold/Elixir/Dark: Minimum resources to attack\n"),
            ("normal", "• Set to 0 to ignore that resource\n\n"),

            ("section", "TIMEOUTS:\n"),
            ("normal", "• Base Search: Max time looking for suitable base\n"),
            ("normal", "• Return Home: Max time waiting for return button\n\n"),

            ("header", "🗺️ DEPLOYMENT MAP TAB\n"),
            ("normal", "Shows your base with deployment location markers:\n"),
            ("normal", "🔴 Red dots = Troop deployment locations\n"),
            ("normal", "🔵 Blue dots = Spell deployment locations\n"),
            ("normal", "🟢 Green dots = Hero deployment locations\n\n"),

            ("section", "EDITING LOCATIONS:\n"),
            ("normal", "1. Select location type (Troop/Spell/Hero)\n"),
            ("normal", "2. Click row in table to select\n"),
            ("normal", "3. Edit X/Y values, click 'Update'\n"),
            ("normal", "4. Or click 'Delete' to remove\n\n"),

            ("section", "ADDING NEW LOCATIONS:\n"),
            ("normal", "1. Click on map to get coordinates, OR\n"),
            ("normal", "2. Enter X,Y in the input fields\n"),
            ("normal", "3. Click '+ Troop', '+ Spell', or '+ Hero'\n"),
            ("normal", "4. Save by clicking 'Save Settings' in Settings tab\n\n"),

            ("header", "📋 BOT FLOW ORDER\n"),
            ("normal", "1. Collect Gold (if enabled)\n"),
            ("normal", "2. Collect Elixir (if enabled)\n"),
            ("normal", "3. Collect Dark Elixir (if enabled)\n"),
            ("normal", "4. Navigate to Attack screen\n"),
            ("normal", "5. Find Match (if enabled)\n"),
            ("normal", "6. Search for Base (if enabled)\n"),
            ("indent", "   - Skips bases below thresholds\n"),
            ("normal", "7. Deploy Troops (if enabled)\n"),
            ("normal", "8. Deploy Heroes (if enabled)\n"),
            ("normal", "9. Deploy Spells (if enabled)\n"),
            ("normal", "10. Trigger Abilities (if enabled)\n"),
            ("normal", "11. Return Home (if enabled)\n"),
            ("normal", "12. Repeat from step 1\n\n"),

            ("header", "🔧 TROUBLESHOOTING\n"),
            ("section", "Q: Bot doesn't find my device\n"),
            ("normal", "A: Run 'adb devices' in terminal. Enable USB debugging.\n\n"),

            ("section", "Q: Troops deploy at wrong locations\n"),
            ("normal", "A: Go to Deployment Map tab, edit coordinates\n\n"),

            ("section", "Q: Bot skips all bases\n"),
            ("normal", "A: Lower resource thresholds in Settings tab\n\n"),

            ("section", "Q: Bot won't stop\n"),
            ("normal", "A: Wait for current loop, or restart GUI\n\n"),

            ("section", "Q: Screenshot shows blank/wrong\n"),
            ("normal", "A: Click 'Refresh Screenshot' button\n\n"),

            ("section", "Q: Where are logs saved?\n"),
            ("normal", "A: bot_session_log.txt in project folder\n\n"),

            ("header", "📸 ADDING NEW SCREENSHOTS\n"),
            ("normal", "UI templates are stored in: ui_main_base/\n\n"),
            ("normal", "To add a new button/target:\n"),
            ("normal", "1. Take screenshot of your game\n"),
            ("normal", "2. Crop the specific button area\n"),
            ("normal", "3. Save as PNG in appropriate folder:\n"),
            ("indent", "   - ui_main_base/attack_button/\n"),
            ("indent", "   - ui_main_base/gold_collect/\n"),
            ("indent", "   - ui_main_base/troops/super_minion/\n"),
            ("indent", "   - etc.\n"),
            ("normal", "4. Bot will auto-detect it next run\n\n"),

            ("header", "💡 TIPS\n"),
            ("normal", "• Use lower resource thresholds for more attacks\n"),
            ("normal", "• More troop locations = more spread out deployment\n"),
            ("normal", "• Random offsets make clicks appear more human-like\n"),
            ("normal", "• Check bot_session_log.txt for detailed history\n"),
        ]

        self.text.configure(state=tk.NORMAL)
        for style, text in content:
            self.text.insert(tk.END, text, (style, "gap"))
        self.text.configure(state=tk.DISABLED)
        self.text.yview_moveto(0)
