#!/usr/bin/env python3
"""
CoC Bot GUI - Main Window
Tkinter GUI for the CoC Bot with settings management and deployment visualization.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess
from datetime import datetime
from typing import Optional

from bot import CoCBot
from utils.device import DeviceController
from deployment_config import DeploymentConfig
import config


class LogCapture:
    """Captures log output to both file and GUI callback."""

    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.callback = None
        self._start_session()

    def _start_session(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""
╔══════════════════════════════════════════════════════════════╗
║              CoC BOT SESSION - {timestamp:<28}║
╚══════════════════════════════════════════════════════════════╝
"""
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(header)
        self._emit("Bot session started", "INFO")

    def _emit(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level:5}] {message}"
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
        if self.callback:
            self.callback(formatted)

    def info(self, message: str):
        self._emit(message, "INFO")

    def warning(self, message: str):
        self._emit(message, "WARN")

    def error(self, message: str):
        self._emit(message, "ERROR")


class CoCGUI:
    """Main GUI class that orchestrates all tabs."""

    CANVAS_MIN_WIDTH = 400
    CANVAS_MIN_HEIGHT = 600

    def __init__(self):
        self.bot: Optional[CoCBot] = None
        self.bot_thread: Optional[threading.Thread] = None
        self.running = False
        self.deploy_config = DeploymentConfig()
        self.log_capture = LogCapture(config.LOG_FILE)
        self.flow_state = config.FLOW_CONFIG.copy()

        # GUI refs
        self.window: Optional[tk.Tk] = None
        self.notebook: Optional[ttk.Notebook] = None
        self.log_text: Optional[tk.Text] = None
        self.status_label: Optional[ttk.Label] = None
        self.loop_label: Optional[ttk.Label] = None
        self.gold_label: Optional[ttk.Label] = None
        self.elixir_label: Optional[ttk.Label] = None
        self.dark_label: Optional[ttk.Label] = None
        self.runtime_label: Optional[ttk.Label] = None
        self.toggle_button: Optional[ttk.Button] = None
        self.device_combo: Optional[ttk.Combobox] = None
        self.flow_vars = {}
        self.webhook_entry: Optional[ttk.Entry] = None

        # Settings refs
        self.settings_entries = {}
        self.troop_vars = {}
        self.troop_count_vars = {}
        self.spell_vars = {}
        self.spell_count_vars = {}
        self.hero_vars = {}
        self.hero_count_vars = {}

        # Deploy map refs
        self.screenshot_canvas: Optional[tk.Canvas] = None
        self.screenshot_image: Optional[tk.PhotoImage] = None
        self.location_table: Optional[ttk.Treeview] = None
        self.loc_type_var: Optional[tk.StringVar] = None
        self.selected_loc_index: Optional[int] = None
        self.selected_loc_type: Optional[str] = None
        self.add_coords = None
        self.img_scale = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0
        self._window_ready = False
        self._resize_after_id = None

        self._build_window()

    def _get_devices(self) -> list[str]:
        try:
            result = subprocess.run(
                ["adb", "devices"], capture_output=True, text=True, check=True
            )
            devices = [
                line.split("\t")[0]
                for line in result.stdout.strip().split("\n")[1:]
                if line.strip() and "\tdevice" in line
            ]
            return devices if devices else ["No devices"]
        except subprocess.CalledProcessError:
            return ["ADB Error"]

    def _build_window(self):
        self.window = tk.Tk()
        self.window.title("⚔️  CoC Bot Control Center")
        self.window.geometry("1000x780")
        self.window.configure(bg="#1e1e1e")
        self.window.resizable(True, True)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background="#1e1e1e", foreground="#ffffff")
        style.configure("TFrame", background="#1e1e1e", foreground="#ffffff")
        style.configure("Dark.TFrame", background="#2d2d2d", foreground="#ffffff")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        style.configure("Dark.TLabel", background="#1e1e1e", foreground="#ffffff")
        style.configure("TLabelframe", background="#2d2d2d", foreground="#ffffff")
        style.configure("TLabelframe.Label", background="#2d2d2d", foreground="#ffffff")
        style.configure("Header.TLabel", font=("Consolas", 11, "bold"), background="#1e1e1e", foreground="#ffffff")
        style.configure("Status.TLabel", font=("Consolas", 14, "bold"), background="#1e1e1e", foreground="#00ff00")
        style.configure("TButton", font=("Consolas", 10), foreground="#ffffff")
        style.configure("Start.TButton", font=("Consolas", 12, "bold"), foreground="#ffffff")
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#ffffff")
        style.configure("TRadiobutton", background="#1e1e1e", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#2d2d2d", background="#2d2d2d", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#2d2d2d", foreground="#ffffff", insertcolor="#ffffff")
        style.configure("TSpinbox", fieldbackground="#2d2d2d", foreground="#ffffff", insertcolor="#ffffff")
        style.configure("Treeview", background="#2d2d2d", foreground="#ffffff", fieldbackground="#2d2d2d")
        style.configure("Treeview.Heading", background="#1e1e1e", foreground="#ffffff")
        style.configure("TNotebook", background="#1e1e1e")
        style.configure("TNotebook.Tab", background="#2d2d2d", foreground="#ffffff")

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Import and create tab classes
        from gui_pkg.control_tab import ControlTab
        from gui_pkg.settings_tab import SettingsTab
        from gui_pkg.deploy_map_tab import DeployMapTab
        from gui_pkg.help_tab import HelpTab

        self.control_tab = ControlTab(self.notebook, self)
        self.settings_tab = SettingsTab(self.notebook, self)
        self.deploy_map_tab = DeployMapTab(self.notebook, self)
        self.help_tab = HelpTab(self.notebook, self)

        self.log_capture.callback = self._append_log
        self.window.after_idle(self._on_window_ready)

    def _on_window_ready(self):
        self._window_ready = True
        self.deploy_map_tab.refresh_location_table()
        self.window.after(200, self.deploy_map_tab.delayed_screenshot_init)

    def _append_log(self, message: str):
        if self.log_text:
            tag = "ERROR" if "[ERROR]" in message else "WARN" if "[WARN]" in message else "INFO"
            def _update():
                try:
                    self.log_text.configure(state=tk.NORMAL)
                    self.log_text.insert(tk.END, message + "\n", tag)
                    self.log_text.see(tk.END)
                    self.log_text.configure(state=tk.DISABLED)
                except tk.TclError:
                    pass
            self.log_text.after(0, _update)

    def _update_stats(self, loop: int, gold: int, elixir: int, dark: int, runtime: str):
        if self.loop_label:
            self.loop_label.config(text=str(loop))
        if self.gold_label:
            self.gold_label.config(text=f"{gold:,}")
        if self.elixir_label:
            self.elixir_label.config(text=f"{elixir:,}")
        if self.dark_label:
            self.dark_label.config(text=f"{dark:,}")
        if self.runtime_label:
            self.runtime_label.config(text=runtime)

    def _update_status(self, status: str, color: str):
        if self.status_label:
            self.status_label.config(text=f"● {status}", foreground=color)

    def _update_toggle_button(self, running: bool):
        if self.toggle_button:
            text = "■  STOP BOT" if running else "▶  START BOT"
            self.toggle_button.config(text=text)

    def _get_flow_config(self) -> dict:
        return {name: var.get() for name, var in self.flow_vars.items()}

    def _refresh_devices(self) -> None:
        """Refresh device list."""
        devices = self._get_devices()
        if self.device_combo:
            self.device_combo["values"] = devices
            if devices:
                self.device_combo.current(0)
        self.log_capture.info(f"Devices refreshed: {devices}")

    def _toggle_bot(self):
        if self.running:
            self._stop_bot()
        else:
            self._start_bot()

    def _start_bot(self):
        device_id = self.device_combo.get() if self.device_combo else None
        webhook = self.webhook_entry.get() if self.webhook_entry else ""
        flow = self._get_flow_config()

        if device_id in ["No devices", "ADB Error", ""]:
            self.log_capture.error("No valid device selected!")
            return

        self.log_capture.info(f"Starting bot on device: {device_id}")
        config.FLOW_CONFIG.update(flow)
        self.settings_tab.save_settings_to_config()

        device = DeviceController(device_id=device_id)
        self.bot = CoCBot(device_controller=device, webhook_url=webhook, deployment_config=self.deploy_config)

        original_print = print
        def captured_print(*args, **kwargs):
            msg = " ".join(str(a) for a in args)
            original_print(msg)
            self.log_capture.info(msg)

        self.bot_thread = threading.Thread(target=self._bot_worker, args=(captured_print,), daemon=True)
        self.bot_thread.start()

        self.running = True
        self._update_status("RUNNING", "green")
        self._update_toggle_button(True)
        self.log_capture.info("Bot started successfully!")

    def _bot_worker(self, print_func):
        try:
            import builtins
            original_print = builtins.print
            builtins.print = print_func
            self.bot.run()
        except Exception as e:
            self.log_capture.error(f"Bot error: {e}")
        finally:
            self.running = False
            if self.status_label:
                self.status_label.after(0, lambda: self._update_status("STOPPED", "gray"))
            if self.toggle_button:
                self.toggle_button.after(0, lambda: self._update_toggle_button(False))
            import builtins
            builtins.print = original_print

    def _stop_bot(self):
        if self.bot:
            self.bot.stop()
        self.log_capture.warning("Stop requested - bot will stop after current loop")
        self._update_status("STOPPING...", "yellow")

    def run(self):
        last_stats_update = time.time()

        def update_loop():
            nonlocal last_stats_update
            if self.running and self.bot and time.time() - last_stats_update > 1.0:
                elapsed = int(time.time() - self.bot.start_time)
                h, rem = divmod(elapsed, 3600)
                m, s = divmod(rem, 60)
                self._update_stats(self.bot.loop_count, self.bot.session_gold,
                                   self.bot.session_elixir, self.bot.session_dark,
                                   f"{h:02d}:{m:02d}:{s:02d}")
                last_stats_update = time.time()
            if self.window:
                self.window.after(100, update_loop)

        update_loop()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.window.mainloop()

    def _on_close(self):
        if self.running:
            self.log_capture.warning("Closing while bot running...")
        self.window.destroy()


def main():
    print("Starting CoC Bot GUI...")
    gui = CoCGUI()
    gui.run()


if __name__ == "__main__":
    main()
