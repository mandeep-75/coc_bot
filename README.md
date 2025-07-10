# coc Bot (Terminal-Based)

This is a **personal-use coc bot** built to automate attacks in both **Main Village** and **Builder Base**.  
It is designed to run fully from the **terminal (no GUI)** using **ADB + image recognition**.  
Optimized for farming, trophy pushing, and hands-free gameplay.

---

## 🔧 Features

- 🏰 **Base Searching**
  - Searches for enemy bases using loot or trophy criteria.
  - Set minimum loot threshold (Gold, Elixir, Dark Elixir).
  - Can perform **11–13+ attacks** per 30min, more if thresholds are low.

- ⚔️ **Troop Deployment**
  - Smart deployment logic for farming or trophy pushing.
  - Works best with optimized army compositions.
  - Avoids poor bases, improving chances of consistent wins.

- 🏆 **Trophy Pushing Support**
  - If your army composition is strong, the bot avoids losses.
  - Can help **push trophies** while maintaining positive win/loss ratio.

- 🏗️ **Builder Base Support**
  - Supports automated Builder Base battles.
  - Base detection and troop drop timing optimized for Builder mode.

- 🎯 **Custom Threshold Settings**
  - Set loot threshold
  - Lower thresholds = more frequent matches and faster farming.

- 🖥️ **Terminal-Based Only**
  - Simple, fast, and lightweight.
  - No GUI, no mouse simulation — just clean CLI execution.

---

## 📦 Requirements

- Python 3.9+
- ADB (Android Debug Bridge)
- OpenCV (`cv2`)
- NumPy
- Pillow

