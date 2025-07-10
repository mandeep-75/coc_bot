import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import random
import os
from PIL import Image, ImageTk
import sys

# Constants for UI styling
BG_COLOR = "#1a1a2e"
ACCENT_COLOR = "#3498db"
SECONDARY_COLOR = "#2c3e50"
TEXT_COLOR = "#ecf0f1"
BUTTON_COLOR = "#3498db"
BUTTON_HOVER = "#2980b9"
STOP_COLOR = "#e74c3c"
PROGRESS_COLOR = "#3498db"
RESOURCE_GOLD = "#f1c40f"
RESOURCE_ELIXIR = "#9b59b6"
RESOURCE_DARK = "#8e44ad"

# Mock resource detection function
def get_resource_values(image_path):
    return {
        'gold': random.randint(50000, 1200000),
        'elixir': random.randint(50000, 1200000),
        'dark_elixir': random.randint(1000, 20000)
    }

class BotWorker(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.running = True
        self.daemon = True
        
    def run(self):
        loop_count = 0
        while self.running:
            try:
                loop_count += 1
                self.app.log_message(f"\n=== Starting Main Base Loop {loop_count} ===")
                
                # Simulate bot operations
                self.app.update_status("Collecting resources...")
                time.sleep(1)
                
                # Simulate resource detection
                resources = {
                    'gold': random.randint(50000, 1200000),
                    'elixir': random.randint(50000, 1200000),
                    'dark_elixir': random.randint(1000, 20000)
                }
                self.app.update_resources(resources)
                
                # Check resource thresholds
                if (resources['gold'] >= self.app.gold_threshold.get() and 
                    resources['elixir'] >= self.app.elixir_threshold.get() and
                    resources['dark_elixir'] >= self.app.dark_threshold.get()):
                    self.app.log_message("Resource thresholds met. Starting attack...")
                    
                    # Simulate attack sequence
                    self.app.update_status("Finding match...")
                    time.sleep(1.5)
                    
                    if self.app.use_super_minion.get():
                        self.app.log_message("Deploying Super Minions...")
                        time.sleep(0.5)
                    
                    if self.app.use_rage_spell.get():
                        self.app.log_message("Deploying Rage Spells...")
                        time.sleep(0.5)
                    
                    if self.app.use_ice_spell.get():
                        self.app.log_message("Deploying Ice Spells...")
                        time.sleep(0.5)
                    
                    if self.app.hero_deployment.get():
                        self.app.log_message("Deploying Heroes...")
                        time.sleep(1)
                    
                    self.app.update_status("Attack in progress...")
                    time.sleep(5)
                    
                    self.app.update_status("Attack complete. Returning home...")
                    time.sleep(1)
                    self.app.increment_attack_count()
                else:
                    self.app.log_message("Resource thresholds not met. Skipping attack.")
                
                # Update loop counter
                self.app.loop_count.set(loop_count)
                
                time.sleep(2)
                
            except Exception as e:
                self.app.log_message(f"Error in main base loop: {e}")
                time.sleep(2)
    
    def stop(self):
        self.running = False
        self.app.update_status("Bot stopped")

class ClashBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clash of Clans Bot")
        self.root.geometry("1100x750")
        self.root.configure(bg=BG_COLOR)
        
        # Initialize variables
        self.loop_count = tk.IntVar(value=0)
        self.attack_count = tk.IntVar(value=0)
        self.collection_count = tk.IntVar(value=0)
        self.gold_threshold = tk.IntVar(value=900000)
        self.elixir_threshold = tk.IntVar(value=900000)
        self.dark_threshold = tk.IntVar(value=10000)
        self.use_super_minion = tk.BooleanVar(value=True)
        self.use_rage_spell = tk.BooleanVar(value=True)
        self.use_ice_spell = tk.BooleanVar(value=False)
        self.hero_deployment = tk.BooleanVar(value=True)
        
        # Create bot worker
        self.bot_worker = None
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure('TButton', background=BUTTON_COLOR, foreground=TEXT_COLOR, 
                         borderwidth=1, focusthickness=3, focuscolor='none')
        style.map('TButton', background=[('active', BUTTON_HOVER)])
        style.configure('Red.TButton', background=STOP_COLOR)
        style.map('Red.TButton', background=[('active', '#c0392b')])
        style.configure('TProgressbar', background=PROGRESS_COLOR, troughcolor=SECONDARY_COLOR)
        style.configure('TCheckbutton', background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure('TRadiobutton', background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure('TCombobox', fieldbackground=SECONDARY_COLOR, background=SECONDARY_COLOR)
        style.configure('TEntry', fieldbackground=SECONDARY_COLOR)
        style.configure('TScrolledText', background=SECONDARY_COLOR, foreground=TEXT_COLOR)
        
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(header_frame, text="CLASH OF CLANS BOT", 
                               font=('Arial', 20, 'bold'), foreground=ACCENT_COLOR)
        title_label.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(header_frame, text="Status: Ready", font=('Arial', 10))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Resource display
        resource_frame = ttk.Frame(self.root)
        resource_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.gold_label = ttk.Label(resource_frame, text="Gold: 0", foreground=RESOURCE_GOLD, 
                                   font=('Arial', 10, 'bold'))
        self.gold_label.pack(side=tk.LEFT, padx=10)
        
        self.elixir_label = ttk.Label(resource_frame, text="Elixir: 0", foreground=RESOURCE_ELIXIR, 
                                     font=('Arial', 10, 'bold'))
        self.elixir_label.pack(side=tk.LEFT, padx=10)
        
        self.dark_label = ttk.Label(resource_frame, text="Dark Elixir: 0", foreground=RESOURCE_DARK, 
                                   font=('Arial', 10, 'bold'))
        self.dark_label.pack(side=tk.LEFT, padx=10)
        
        # Main content area
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Controls
        left_frame = ttk.Frame(main_paned, width=350)
        main_paned.add(left_frame, weight=1)
        
        # Threshold Settings
        threshold_frame = ttk.LabelFrame(left_frame, text="Resource Thresholds")
        threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Gold Threshold:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        gold_entry = ttk.Entry(threshold_frame, textvariable=self.gold_threshold, width=10)
        gold_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Elixir Threshold:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        elixir_entry = ttk.Entry(threshold_frame, textvariable=self.elixir_threshold, width=10)
        elixir_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Dark Elixir Threshold:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        dark_entry = ttk.Entry(threshold_frame, textvariable=self.dark_threshold, width=10)
        dark_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Deployment Settings
        deploy_frame = ttk.LabelFrame(left_frame, text="Deployment Settings")
        deploy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(deploy_frame, text="Use Super Minion", variable=self.use_super_minion).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(deploy_frame, text="Use Rage Spell", variable=self.use_rage_spell).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(deploy_frame, text="Use Ice Spell", variable=self.use_ice_spell).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(deploy_frame, text="Enable Hero Deployment", variable=self.hero_deployment).pack(anchor=tk.W, padx=5, pady=2)
        
        strategy_frame = ttk.Frame(deploy_frame)
        strategy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(strategy_frame, text="Deployment Strategy:").pack(side=tk.LEFT, padx=(0, 5))
        self.strategy_combo = ttk.Combobox(strategy_frame, values=["Balanced", "Aggressive", "Defensive", "Resource Focus"], 
                                          state="readonly", width=15)
        self.strategy_combo.pack(side=tk.LEFT)
        self.strategy_combo.current(0)
        
        # Control buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Bot", style='Red.TButton', 
                                    command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Collect Resources", command=self.collect_resources).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Attack", command=self.start_attack).pack(side=tk.LEFT, padx=5)
        
        # Progress indicators
        progress_frame = ttk.LabelFrame(left_frame, text="Operation Progress")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(progress_frame, text="Completed Loops:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        loop_label = ttk.Label(progress_frame, textvariable=self.loop_count)
        loop_label.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(progress_frame, text="Attacks Performed:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        attack_label = ttk.Label(progress_frame, textvariable=self.attack_count)
        attack_label.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(progress_frame, text="Resource Collections:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        collect_label = ttk.Label(progress_frame, textvariable=self.collection_count)
        collect_label.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, 
                                           mode='determinate', length=300)
        self.progress_bar.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky=tk.W+tk.E)
        
        # Right panel - Log and Screenshot
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # Screenshot display
        screenshot_frame = ttk.LabelFrame(right_frame, text="Current View")
        screenshot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a canvas for the screenshot display
        self.canvas = tk.Canvas(screenshot_frame, bg=SECONDARY_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Placeholder for screenshot
        self.draw_mock_screenshot()
        
        # Log area
        log_frame = ttk.LabelFrame(right_frame, text="Activity Log")
        log_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, bg=SECONDARY_COLOR, fg=TEXT_COLOR)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.config(state=tk.DISABLED)
        
        # Log buttons
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(log_button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_button_frame, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # Footer
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(footer_frame, text="Clash of Clans Bot v1.0 | Developed for COC Automation", 
                 font=('Arial', 8)).pack(side=tk.LEFT)
        
        # Initialize resource display
        self.update_resources({'gold': 0, 'elixir': 0, 'dark_elixir': 0})
        
    def draw_mock_screenshot(self):
        """Draw a mock Clash of Clans scene on the canvas"""
        self.canvas.delete("all")
        
        # Load and display a placeholder image
        self.placeholder_image = ImageTk.PhotoImage(Image.new("RGB", (800, 600), color=SECONDARY_COLOR))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.placeholder_image)
        
    
    def log_message(self, message):
        """Add a message to the log area with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)
        
    def clear_log(self):
        """Clear the log area"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.log_message("Log cleared")
        
    def save_log(self):
        """Save the log content to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.log_area.get(1.0, tk.END))
                self.log_message(f"Log saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {str(e)}")
    
    def update_status(self, status):
        """Update the status label"""
        self.status_label.config(text=f"Status: {status}")
        self.log_message(status)
        
    def update_resources(self, resources):
        """Update the resource display"""
        self.gold_label.config(text=f"Gold: {resources['gold']:,}")
        self.elixir_label.config(text=f"Elixir: {resources['elixir']:,}")
        self.dark_label.config(text=f"Dark Elixir: {resources['dark_elixir']:,}")
        
    def increment_attack_count(self):
        """Increment the attack counter"""
        self.attack_count.set(self.attack_count.get() + 1)
        
    def start_bot(self):
        """Start the bot worker thread"""
        if self.bot_worker and self.bot_worker.is_alive():
            self.log_message("Bot is already running")
            return
            
        self.log_message("Starting bot...")
        self.update_status("Initializing...")
        
        self.bot_worker = BotWorker(self)
        self.bot_worker.start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar["value"] = 50
        
    def stop_bot(self):
        """Stop the bot worker thread"""
        if self.bot_worker:
            self.bot_worker.stop()
            self.log_message("Stopping bot...")
            self.update_status("Stopping...")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_bar["value"] = 0
            
    def collect_resources(self):
        """Simulate resource collection"""
        self.log_message("Collecting resources...")
        self.collection_count.set(self.collection_count.get() + 1)
        self.update_status("Resource collection in progress")
        
    def start_attack(self):
        """Simulate manual attack"""
        self.log_message("Starting manual attack...")
        self.attack_count.set(self.attack_count.get() + 1)
        self.update_status("Manual attack in progress")
        
    def on_closing(self):
        """Handle window closing event"""
        if self.bot_worker and self.bot_worker.is_alive():
            self.bot_worker.stop()
            self.bot_worker.join(1.0)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClashBotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()