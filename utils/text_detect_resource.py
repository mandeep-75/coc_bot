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

def get_image_values(image, filter="null"):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_blur = cv2.GaussianBlur(image_gray, (5, 5), 0)
    image_text = pytesseract.image_to_string(image_blur,config='--psm 7 -c tessedit_char_whitelist=0123456789')
    image_value = re.sub(r'\D', '', image_text)

    if not image_value:
        return 0

    image_value = int(image_value)

    if filter == "dark_elixir" and image_value >= 50:
        return 0

    return image_value


def get_resource_values(screenshot_path):
    img = cv2.imread(screenshot_path)
    if img is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return None
    # Wider bounding boxes for resource detection (x1, y1, x2, y2)
    gold_bbox = (65, 95, 200, 120)   # Top left region - Gold
    elixir_bbox =(65, 135, 200, 160) # Top center region - Elixir
    dark_bbox = (65, 175, 150, 200)   # Top right region - Dark Elixir
    trophies_bbox = (62, 231, 108, 254) # Bottom left region - Trophies 
    # Crop regions
    gold_region = img[gold_bbox[1]:gold_bbox[3], gold_bbox[0]:gold_bbox[2]]
    elixir_region = img[elixir_bbox[1]:elixir_bbox[3], elixir_bbox[0]:elixir_bbox[2]]
    dark_region = img[dark_bbox[1]:dark_bbox[3], dark_bbox[0]:dark_bbox[2]]
    trophies_region = img[trophies_bbox[1]:trophies_bbox[3], trophies_bbox[0]:trophies_bbox[2]]

    gold_value = get_image_values(gold_region)
    elixir_value = get_image_values(elixir_region)
    dark_value = get_image_values(dark_region)
    trophies_value = get_image_values(trophies_region,"dark_elixir")

    print(f"Gold: {gold_value}, Elixir: {elixir_value}, Dark Elixir: {dark_value}, Trophies: {trophies_value}")
    return {'gold': gold_value, 'elixir': elixir_value, 'dark_elixir': dark_value , 'trophies': trophies_value}

if __name__ == "__main__":
    # Example usage
    get_resource_values("screen.png") 