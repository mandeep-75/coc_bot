import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import queue
import threading
from main import BotConfig, ClashBot

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

class ClashBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clash of Clans Bot")
        self.root.geometry("800x600")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create settings frame
        self.settings_frame = ttk.LabelFrame(self.main_container, text="Settings", padding="5")
        self.settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=5, pady=5)
        
        # Create settings grid
        self.create_settings_grid()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Create log frame
        self.log_frame = ttk.LabelFrame(self.main_container, text="Log", padding="5")
        self.log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Create log text widget
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        # Initialize bot variables
        self.bot = None
        self.bot_thread = None
        self.log_queue = queue.Queue()
        self.setup_logging()
        
        # Add status check timer
        self.status_check_timer = None
        
    def create_settings_grid(self):
        # General Settings
        ttk.Label(self.settings_frame, text="General Settings").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Debug Mode
        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.settings_frame, text="Debug Mode", variable=self.debug_var).grid(row=1, column=0, sticky=tk.W)
        
        # Max Cycles
        ttk.Label(self.settings_frame, text="Max Cycles:").grid(row=2, column=0, sticky=tk.W)
        self.max_cycles_var = tk.StringVar(value="")
        ttk.Entry(self.settings_frame, textvariable=self.max_cycles_var, width=10).grid(row=2, column=1, sticky=tk.W)
        
        # Cycle Delay
        ttk.Label(self.settings_frame, text="Cycle Delay (s):").grid(row=3, column=0, sticky=tk.W)
        self.cycle_delay_var = tk.StringVar(value="2.0")
        ttk.Entry(self.settings_frame, textvariable=self.cycle_delay_var, width=10).grid(row=3, column=1, sticky=tk.W)
        
        # Sequence Toggles
        ttk.Label(self.settings_frame, text="Sequence Toggles").grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.enable_starting_var = tk.BooleanVar(value=True)
        self.enable_searching_var = tk.BooleanVar(value=True)
        self.enable_attacking_var = tk.BooleanVar(value=True)
        self.enable_donations_var = tk.BooleanVar(value=False)
        self.enable_wall_upgrades_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(self.settings_frame, text="Enable Starting", variable=self.enable_starting_var).grid(row=5, column=0, sticky=tk.W)
        ttk.Checkbutton(self.settings_frame, text="Enable Searching", variable=self.enable_searching_var).grid(row=6, column=0, sticky=tk.W)
        ttk.Checkbutton(self.settings_frame, text="Enable Attacking", variable=self.enable_attacking_var).grid(row=7, column=0, sticky=tk.W)
        ttk.Checkbutton(self.settings_frame, text="Enable Donations", variable=self.enable_donations_var).grid(row=8, column=0, sticky=tk.W)
        ttk.Checkbutton(self.settings_frame, text="Enable Wall Upgrades", variable=self.enable_wall_upgrades_var).grid(row=9, column=0, sticky=tk.W)
        
        # Resource Thresholds
        ttk.Label(self.settings_frame, text="Resource Thresholds").grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Gold Threshold
        ttk.Label(self.settings_frame, text="Gold:").grid(row=11, column=0, sticky=tk.W)
        self.gold_threshold_var = tk.StringVar(value="1000000")
        ttk.Entry(self.settings_frame, textvariable=self.gold_threshold_var, width=10).grid(row=11, column=1, sticky=tk.W)
        
        # Elixir Threshold
        ttk.Label(self.settings_frame, text="Elixir:").grid(row=12, column=0, sticky=tk.W)
        self.elixir_threshold_var = tk.StringVar(value="1000000")
        ttk.Entry(self.settings_frame, textvariable=self.elixir_threshold_var, width=10).grid(row=12, column=1, sticky=tk.W)
        
        # Dark Threshold
        ttk.Label(self.settings_frame, text="Dark:").grid(row=13, column=0, sticky=tk.W)
        self.dark_threshold_var = tk.StringVar(value="5000")
        ttk.Entry(self.settings_frame, textvariable=self.dark_threshold_var, width=10).grid(row=13, column=1, sticky=tk.W)
        
        # Attack Settings
        ttk.Label(self.settings_frame, text="Attack Settings").grid(row=14, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Target Percentage
        ttk.Label(self.settings_frame, text="Target %:").grid(row=15, column=0, sticky=tk.W)
        self.target_percentage_var = tk.StringVar(value="50")
        ttk.Entry(self.settings_frame, textvariable=self.target_percentage_var, width=10).grid(row=15, column=1, sticky=tk.W)
        
        # Max Searches
        ttk.Label(self.settings_frame, text="Max Searches:").grid(row=16, column=0, sticky=tk.W)
        self.max_searches_var = tk.StringVar(value="30000")
        ttk.Entry(self.settings_frame, textvariable=self.max_searches_var, width=10).grid(row=16, column=1, sticky=tk.W)
        
        # Donation Settings
        ttk.Label(self.settings_frame, text="Donation Settings").grid(row=17, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Donation Interval
        ttk.Label(self.settings_frame, text="Donation Interval:").grid(row=18, column=0, sticky=tk.W)
        self.donation_interval_var = tk.StringVar(value="3")
        ttk.Entry(self.settings_frame, textvariable=self.donation_interval_var, width=10).grid(row=18, column=1, sticky=tk.W)
        
        # Wall Upgrade Settings
        ttk.Label(self.settings_frame, text="Wall Upgrade Settings").grid(row=19, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Wall Upgrade Interval
        ttk.Label(self.settings_frame, text="Wall Upgrade Interval:").grid(row=20, column=0, sticky=tk.W)
        self.wall_upgrade_interval_var = tk.StringVar(value="5")
        ttk.Entry(self.settings_frame, textvariable=self.wall_upgrade_interval_var, width=10).grid(row=20, column=1, sticky=tk.W)
        
    def create_control_buttons(self):
        self.control_frame = ttk.Frame(self.main_container)
        self.control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.start_button = ttk.Button(self.control_frame, text="Start Bot", command=self.start_bot)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
    def setup_logging(self):
        # Create a handler that puts log records into a queue
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Get the root logger and add the queue handler
        root_logger = logging.getLogger()
        root_logger.addHandler(queue_handler)
        
        # Start the queue processing
        self.process_log_queue()
        
    def process_log_queue(self):
        while True:
            try:
                record = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, self.format_log_record(record) + '\n')
                self.log_text.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self.process_log_queue)
        
    def format_log_record(self, record):
        return f"{record.asctime} - {record.levelname} - {record.getMessage()}"
        
    def get_config(self):
        try:
            max_cycles = int(self.max_cycles_var.get()) if self.max_cycles_var.get() else None
            cycle_delay = float(self.cycle_delay_var.get())
            gold_threshold = int(self.gold_threshold_var.get())
            elixir_threshold = int(self.elixir_threshold_var.get())
            dark_threshold = int(self.dark_threshold_var.get())
            target_percentage = int(self.target_percentage_var.get())
            max_searches = int(self.max_searches_var.get())
            donation_interval = int(self.donation_interval_var.get())
            wall_upgrade_interval = int(self.wall_upgrade_interval_var.get())
            
            return BotConfig(
                debug_mode=self.debug_var.get(),
                max_cycles=max_cycles,
                cycle_delay=cycle_delay,
                enable_starting=self.enable_starting_var.get(),
                enable_searching=self.enable_searching_var.get(),
                enable_attacking=self.enable_attacking_var.get(),
                enable_donations=self.enable_donations_var.get(),
                enable_wall_upgrades=self.enable_wall_upgrades_var.get(),
                target_percentage=target_percentage,
                max_searches=max_searches,
                gold_threshold=gold_threshold,
                elixir_threshold=elixir_threshold,
                dark_threshold=dark_threshold,
                donation_interval=donation_interval,
                wall_upgrade_interval=wall_upgrade_interval
            )
        except ValueError as e:
            logging.error(f"Invalid configuration value: {str(e)}")
            return None
            
    def start_bot(self):
        # Kill any existing bot first
        self.kill_bot()
        
        config = self.get_config()
        if config is None:
            return
            
        # Create new bot instance
        self.bot = ClashBot(config)
        self.bot_thread = threading.Thread(target=self.bot.run)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start status check timer
        self.status_check_timer = self.root.after(1000, self.check_bot_status)
        logging.info("Bot started successfully")
        
    def stop_bot(self):
        self.kill_bot()
        
    def kill_bot(self):
        """Kill the bot immediately without waiting."""
        if self.bot:
            logging.info("Killing bot...")
            self.bot.running = False
            self.bot = None
            self.bot_thread = None
            
            # Cancel status check timer
            if self.status_check_timer:
                self.root.after_cancel(self.status_check_timer)
                self.status_check_timer = None
            
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            logging.info("Bot killed")
            
    def check_bot_status(self):
        """Check if the bot thread is still running and update UI accordingly."""
        if self.bot_thread and self.bot_thread.is_alive():
            # Bot is still running, schedule next check
            self.status_check_timer = self.root.after(1000, self.check_bot_status)
        else:
            # Bot has stopped, update UI
            logging.info("Bot thread has stopped")
            self.bot = None
            self.bot_thread = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Cancel status check timer
            if self.status_check_timer:
                self.root.after_cancel(self.status_check_timer)
                self.status_check_timer = None
                
    def __del__(self):
        """Cleanup when the GUI is destroyed."""
        if self.status_check_timer:
            self.root.after_cancel(self.status_check_timer)
        self.kill_bot()

def main():
    root = tk.Tk()
    app = ClashBotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 