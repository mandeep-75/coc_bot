import argparse
import time
from utils.device import DeviceController
from utils.zoom import zoom_out_pinch, zoom_out_keys, zoom_out_ctrl_scroll

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, help="ADB Device ID")
    parser.add_argument("--method", type=str, choices=['pinch', 'key', 'scroll', 'all'], default='all', help="Zoom method to test")
    args = parser.parse_args()

    controller = DeviceController(device_id=args.device)
    device_id = controller.device_id
    
    if not device_id:
        print("No device found.")
        exit()

    if args.method == 'pinch' or args.method == 'all':
        print("\n--- Testing Pinch Gesture ---")
        zoom_out_pinch(device_id)
        time.sleep(2)

    if args.method == 'key' or args.method == 'all':
        print("\n--- Testing KEYCODE_ZOOM_OUT ---")
        zoom_out_keys(device_id)
        time.sleep(2)

    if args.method == 'scroll' or args.method == 'all':
        print("\n--- Testing Input Scroll (Ctrl+Wheel simulation) ---")
        zoom_out_ctrl_scroll(device_id)
        time.sleep(2)

    print("\nDone. Please check which method worked on your screen.")
