#!/usr/bin/env python3
"""Screenshot tool - Capture device screen and save to desktop."""

import os
import subprocess
import argparse


def get_desktop_path() -> str:
    """Get the desktop path for the current user."""
    home = os.path.expanduser("~")
    if os.name == "nt":  # Windows
        return os.path.join(home, "Desktop")
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            return os.path.join(home, "Desktop")
        else:  # Linux
            return os.path.join(home, "Desktop")
    return home


def take_screenshot(device_id: str = None, output_path: str = None) -> str:
    """Take screenshot from device and save to output path."""
    
    # Build ADB command
    if device_id:
        cmd = ["adb", "-s", device_id, "exec-out", "screencap", "-p"]
    else:
        cmd = ["adb", "exec-out", "screencap", "-p"]
    
    # Determine output path
    if output_path is None:
        desktop = get_desktop_path()
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(desktop, f"screenshot_{timestamp}.png")
    
    # Take screenshot and save
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        with open(output_path, "wb") as f:
            f.write(result.stdout)
        print(f"Screenshot saved to: {output_path}")
        
        # Open the screenshot
        if os.name == "nt":
            os.startfile(output_path)
        elif "darwin" in os.uname().sysname.lower():
            subprocess.run(["open", output_path])
        else:
            subprocess.run(["xdg-open", output_path])
        
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error taking screenshot: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Take device screenshot to desktop")
    parser.add_argument("--device", "-d", type=str, help="ADB device ID")
    parser.add_argument("--output", "-o", type=str, help="Output file path (default: desktop)")
    args = parser.parse_args()
    
    take_screenshot(device_id=args.device, output_path=args.output)


if __name__ == "__main__":
    main()
