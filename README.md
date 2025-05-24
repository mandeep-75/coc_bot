# CoC Bot Personal

A fully automated Clash of Clans bot that handles everything efficiently, including army training, spell management, and attacking. It is optimized to perform 20-25 attacks per hour , with a 90% success rate. Attack failures usually occur only against higher-level Town Halls.

# Features

Fully automated: , army deployment, and attacks.

High success rate: 90% of attacks secure at least one star.


# Army Composition

This setup is best for achieving 50% destruction or securing one star:

Super Minions × 25

Rage Spells × 5

Freeze Spell × 1 (not recomended due to hardcoded)


# ⚠️ Caution

Device Compatibility: The bot relies on cv2 (OpenCV) for image detection, which may not work correctly on different screen sizes or if UI scaling is changed.

Predefined Deployment: Army deployment is based on specific screen coordinates. You may need to update them to use this bot on other devices.


Initial Setup

# 1️⃣ Prerequisites

USB Debugging & Developer Options: Enable these on your mobile device.

ADB (Android Debug Bridge): Ensure ADB is installed and working on your system.


# 2️⃣ How to Run

1. Open Clash of Clans but do not interact with the game.


2. Connect your device via USB.


3. Run the script on your computer.


4. The bot will automaticall start working.

# 3️⃣ Requirements

- Python 3.9+
- opencv-python
- numpy
- pytesseract
- adb (Android Debug Bridge)

Install dependencies:

```bash
pip install -r requirements.txt
```

# coc_bot
