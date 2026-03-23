import cv2
import numpy as np
import subprocess

SCREENSHOT_NAME = "screen.png"


def take_screenshot():
    """Take screenshot from device."""
    device_id = None
    cmd = ["adb", "devices"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    devices = [line.split('\t')[0] for line in result.stdout.strip().split('\n')[1:]
               if line.strip() and '\tdevice' in line]
    if devices:
        device_id = devices[0]
    
    cmd = ["adb", "-s", device_id, "exec-out", "screencap", "-p"] if device_id else ["adb", "exec-out", "screencap", "-p"]
    with open(SCREENSHOT_NAME, "wb") as f:
        subprocess.run(cmd, stdout=f)
    print(f"Screenshot saved: {SCREENSHOT_NAME}")


def visualize_bboxes(screenshot_path: str = None):
    if screenshot_path is None:
        screenshot_path = SCREENSHOT_NAME
    """Visualize resource detection bounding boxes on screenshot."""
    img = cv2.imread(screenshot_path)
    if img is None:
        print(f"Could not load: {screenshot_path}")
        return

    h, w = img.shape[:2]
    print(f"Image dimensions: {w}x{h}")
    print()

    bboxes = {
        "Gold": (95, 100, 210, 123),
        "Elixir": (95, 140, 200, 160),
        "Dark Elixir": (95, 175, 170, 200),
    }

    colors = {
        "Gold": (0, 255, 0),
        "Elixir": (255, 0, 0),
        "Dark Elixir": (0, 0, 255),
    }

    for name, (x1, y1, x2, y2) in bboxes.items():
        width = x2 - x1
        height = y2 - y1
        color = colors[name]

        print(f"{name}:")
        print(f"  bbox: {bboxes[name]}")
        print(f"  x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        print(f"  width={width}, height={height}")
        print()

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    output_path = "screen_with_bboxes.png"
    cv2.imwrite(output_path, img)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    take_screenshot()
    visualize_bboxes()
