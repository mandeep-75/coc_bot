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
    print("Detected text:", text)
    return text

def get_resource_values(screenshot_path):
    img = cv2.imread(screenshot_path)
    if img is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return None
    # Wider bounding boxes for resource detection (x1, y1, x2, y2)
    gold_bbox = (95, 95, 220, 120)    # Top left region - Gold
    elixir_bbox = (95, 135, 220, 160) # Top center region - Elixir
    dark_bbox = (95, 175, 200, 200)   # Top right region - Dark Elixir
    # Crop regions
    gold_region = img[gold_bbox[1]:gold_bbox[3], gold_bbox[0]:gold_bbox[2]]
    elixir_region = img[elixir_bbox[1]:elixir_bbox[3], elixir_bbox[0]:elixir_bbox[2]]
    dark_region = img[dark_bbox[1]:dark_bbox[3], dark_bbox[0]:dark_bbox[2]]
    # Preprocess and OCR gold
    gold_gray = cv2.cvtColor(gold_region, cv2.COLOR_BGR2GRAY)
    gold_text = pytesseract.image_to_string(gold_gray, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    gold_value = re.sub(r'\D', '', gold_text)
    # Preprocess and OCR elixir
    elixir_gray = cv2.cvtColor(elixir_region, cv2.COLOR_BGR2GRAY)
    elixir_text = pytesseract.image_to_string(elixir_gray, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    elixir_value = re.sub(r'\D', '', elixir_text)
    # Preprocess and OCR dark elixir
    dark_gray = cv2.cvtColor(dark_region, cv2.COLOR_BGR2GRAY)
    dark_text = pytesseract.image_to_string(dark_gray, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    dark_value = re.sub(r'\D', '', dark_text)
    print(f"Gold: {gold_value}, Elixir: {elixir_value}, Dark Elixir: {dark_value}")
    return {'gold': gold_value, 'elixir': elixir_value, 'dark_elixir': dark_value}

if __name__ == "__main__":
    # Example usage
    get_resource_values("screen.png") 