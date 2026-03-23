#!/usr/bin/env python3
"""
Clash of Clans Bot - Main Entry Point
Supports both CLI and GUI modes.
"""
import argparse
import sys
import config
from utils.device import DeviceController
from bot import CoCBot


def run_cli(args):
    """Run in CLI mode."""
    # Initialize Device Controller
    print("Initializing Device Controller...")
    device = DeviceController(device_id=args.device)

    # Initialize Bot
    print("Starting CoC Bot...")
    coc_bot = CoCBot(device_controller=device, webhook_url=args.webhook)

    # Run
    try:
        coc_bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user.")


def run_gui():
    """Run in GUI mode."""
    from gui_pkg import CoCGUI
    gui = CoCGUI()
    gui.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clash of Clans Bot")
    parser.add_argument("--device", type=str, help="ADB Device ID")
    parser.add_argument("--webhook", type=str, help="Discord Webhook URL", 
                       default=config.DISCORD_WEBHOOK_URL)
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    
    args = parser.parse_args()
    
    if args.gui:
        run_gui()
    else:
        run_cli(args)
