import cv2
import numpy as np
import random
import os
from utils.vision import get_static_deployment_points

if __name__ == "__main__":
    SCREENSHOT_PATH = "screen.png"
    OUTPUT_PATH = "debug_output.png"

    if not os.path.exists(SCREENSHOT_PATH):
        print(f"❌ '{SCREENSHOT_PATH}' not found. Please take a screenshot first.")
        # Create a dummy image if none exists (1920x1080 black)
        print("Creating dummy 1920x1080 image to test logic...")
        original_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
    else:
        print(f"Loading {SCREENSHOT_PATH}...")
        original_img = cv2.imread(SCREENSHOT_PATH)
    
    draw_img = original_img.copy()
    h, w = draw_img.shape[:2]

    # Call the static function
    # scale_base=0.7 means the central 70% is treated as "Base", deploy in outer 15%
    points = get_static_deployment_points(draw_img, num_points=100, scale_base=0.7)

    # Visualize the "Base Zone" (Exclusion)
    scale_base = 0.7
    margin_x = int(w * (1 - scale_base) / 2)
    margin_y = int(h * (1 - scale_base) / 2)
    
    # Draw Blue Box showing the assumed base area
    cv2.rectangle(draw_img, (margin_x, margin_y), (w-margin_x, h-margin_y), (255, 0, 0), 2)
    cv2.putText(draw_img, "Assumed Base Area (Safe to Avoid)", (margin_x, margin_y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

    # Draw Spawn Points
    print(f"Generated {len(points)} deployment points.")
    for pt in points:
        cv2.circle(draw_img, pt, 8, (0, 255, 0), -1)   # Green Dot
        cv2.circle(draw_img, pt, 10, (0, 0, 0), 1)     # Outline

    # Save
    cv2.imwrite(OUTPUT_PATH, draw_img)
    print(f"✅ Debug image saved to: {OUTPUT_PATH}")
    print("Open this file to verify the static deployment logic.")
