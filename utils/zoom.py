import subprocess
import time
import threading
import re

def get_screen_resolution(device_id):
    """
    Returns (width, height) of the device.
    """
    cmd = ["adb", "-s", device_id, "shell", "wm", "size"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Output format: "Physical size: 720x1280"
        match = re.search(r'(\d+)x(\d+)', result.stdout)
        if match:
            w, h = int(match.group(1)), int(match.group(2))
            # CoC runs in landscape. If the device reports portrait dimensions (w < h),
            # we swap them to match the game's coordinate system.
            if w < h:
                return h, w
            return w, h
    except Exception as e:
        print(f"⚠️ Failed to get resolution: {e}")
    return 1280, 720 # Fallback default

def swipe(device_id, x1, y1, x2, y2, duration=1000):
    cmd = ["adb", "-s", device_id, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)]
    subprocess.run(cmd)

def zoom_out_pinch(device_id):
    """
    Simulates a pinch-in gesture to zoom out (simulating two fingers).
    Adjusts coordinates based on screen resolution.
    """
    w, h = get_screen_resolution(device_id)
    print(f"🔍 Zooming out using pinch on {device_id} (Screen: {w}x{h})...")
    
    # Calculate relative points (10% from edges -> moving inward to 40%)
    # Finger 1 (Top-Left)
    f1_start_x, f1_start_y = int(w * 0.2), int(h * 0.2)
    f1_end_x, f1_end_y     = int(w * 0.45), int(h * 0.45)
    
    # Finger 2 (Bottom-Right)
    f2_start_x, f2_start_y = int(w * 0.8), int(h * 0.8)
    f2_end_x, f2_end_y     = int(w * 0.55), int(h * 0.55)
    
    # Duration ~1000ms is usually good for zoom
    duration = 1000
    
    t1 = threading.Thread(target=swipe, args=(device_id, f1_start_x, f1_start_y, f1_end_x, f1_end_y, duration))
    t2 = threading.Thread(target=swipe, args=(device_id, f2_start_x, f2_start_y, f2_end_x, f2_end_y, duration))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print("✅ Pinch gesture sent.")

def zoom_out_keys(device_id):
    """
    Uses the native Android ZOOM_OUT keycode (169).
    Also tries Ctrl- (Minus) combination which some emulators map.
    """
    print(f"🔍 Zooming out using Key Events on {device_id}...")
    
    # Method A: KEYCODE_ZOOM_OUT
    cmd = ["adb", "-s", device_id, "shell", "input", "keyevent", "169"]
    subprocess.run(cmd)
    
    # Method B: Ctrl + Minus (113 + 69)
    # This is tricky via pure ADB input keyevent as it doesn't hold.
    # But we can try sending them sequentially or using text? No.
    # Some emulators support keyevent combining via internal mapping, but adb is raw.
    pass

def zoom_out_ctrl_scroll(device_id):
    """
    Attempts to simulate Ctrl + Mouse Wheel Down.
    """
    print(f"🔍 Zooming out using 'input scroll' on {device_id}...")
    try:
        # Check API level or just try
        cmd = ["adb", "-s", device_id, "shell", "input", "scroll", "0", "-10"]
        subprocess.run(cmd)
    except Exception as e:
        pass
