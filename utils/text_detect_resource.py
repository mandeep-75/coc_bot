import cv2
import pytesseract
import numpy as np
import re

def extract_resource_text(screenshot_path):
    img = cv2.imread(screenshot_path)
    if img is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6')
    return text


def normalize_value(value):
    """Normalize OCR’d numbers to realistic Clash of Clans ranges."""
    if value <= 0:
        return 0
    
    # Remove impossible values
    if value > 10_000_000:  # e.g., 4,121,838,060
        # Maybe OCR added extra zeros, try scaling down
        while value > 10_000_000:
            value //= 10
    elif value < 100 and value != 0:
        # Sometimes missing zeros (e.g., 13 -> 13000)
        value *= 1000
    
    # Clip to realistic limits
    return max(0, min(value, 2_000_000))


def get_image_values(image, filter="null"):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_blur = cv2.GaussianBlur(image_gray, (5, 5), 0)
    image_text = pytesseract.image_to_string(
        image_blur, config='--psm 7 -c tessedit_char_whitelist=0123456789'
    )
    image_value = re.sub(r'\D', '', image_text)

    if not image_value:
        return 0

    try:
        image_value = int(image_value)
    except ValueError:
        return 0

    # Dark elixir filter
    if filter == "dark_elixir" and image_value >= 50_000:
        return 0

    # Normalize stupid numbers
    image_value = normalize_value(image_value)
    return image_value


def get_resource_values(screenshot_path):
    img = cv2.imread(screenshot_path)
    if img is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return None

    # Wider bounding boxes for resource detection (x1, y1, x2, y2)
    gold_bbox = (65, 95, 200, 120)    # Gold
    elixir_bbox = (65, 135, 200, 160) # Elixir
    dark_bbox = (65, 175, 170, 200)   # Dark Elixir

    # Crop regions
    gold_region = img[gold_bbox[1]:gold_bbox[3], gold_bbox[0]:gold_bbox[2]]
    elixir_region = img[elixir_bbox[1]:elixir_bbox[3], elixir_bbox[0]:elixir_bbox[2]]
    dark_region = img[dark_bbox[1]:dark_bbox[3], dark_bbox[0]:dark_bbox[2]]

    # Extract and normalize
    gold_value = get_image_values(gold_region)
    elixir_value = get_image_values(elixir_region)
    dark_value = get_image_values(dark_region, filter="dark_elixir")

    return {
        'gold': gold_value,
        'elixir': elixir_value,
        'dark_elixir': dark_value
    }


if __name__ == "__main__":
    result = get_resource_values("screen.png")
    print(result)
