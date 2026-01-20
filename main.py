import argparse
import config
from utils.device import DeviceController
from bot import CoCBot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clash of Clans Bot")
    parser.add_argument("--device", type=str, help="ADB Device ID")
    parser.add_argument("--webhook", type=str, help="Discord Webhook URL", default=config.DISCORD_WEBHOOK_URL)
    args = parser.parse_args()

    # 1. Initialize Device Controller
    print("🤖 Initializing Device Controller...")
    device = DeviceController(device_id=args.device)

    # 2. Initialize Bot
    print("🎮 Starting CoC Bot...")
    coc_bot = CoCBot(device_controller=device, webhook_url=args.webhook)

    # 3. Run
    try:
        coc_bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user.")
