import cv2
import re
import easyocr

import warnings

warnings.filterwarnings("ignore", category=UserWarning)

try:
    import torch

    _gpu_available = bool(
        getattr(torch, "cuda", None) and torch.cuda.is_available()
    ) or bool(
        getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
    )
except Exception:
    _gpu_available = False

_easyocr_reader = easyocr.Reader(["en"], gpu=_gpu_available, verbose=False)


def preprocess_for_ocr(image):
    """Preprocess image for better OCR accuracy."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    return contrast


def get_image_values(image, resource_type="default"):
    """Extract numeric value from an image region."""
    if image is None or image.size == 0:
        return 0

    processed = preprocess_for_ocr(image)

    try:
        results = _easyocr_reader.readtext(processed, detail=0)
    except Exception:
        return 0

    if not results:
        return 0

    concatenated = "".join(str(t) for t in results)
    digits_only = re.sub(r"[^0-9KkMm]", "", concatenated)

    if not digits_only:
        return 0

    text = digits_only.strip().upper()

    if "K" in text:
        text = text.replace("K", "")
        try:
            value = int(float(text) * 1_000)
        except ValueError:
            value = 0
    elif "M" in text:
        text = text.replace("M", "")
        try:
            value = int(float(text) * 1_000_000)
        except ValueError:
            value = 0
    else:
        text = re.sub(r"[^0-9]", "", text)
        try:
            value = int(text)
        except ValueError:
            value = 0

    if value <= 0:
        return 0

    max_values = {
        "gold": 5_000_000,
        "elixir": 5_000_000,
        "dark_elixir": 500_000,
    }
    max_val = max_values.get(resource_type, 5_000_000)

    while value > max_val and value > 0:
        value //= 10

    return max(0, min(value, max_val))


def get_resource_values(screenshot_path):
    """Extract all resource values from a screenshot."""
    img = cv2.imread(screenshot_path)
    if img is None:
        return {"gold": 0, "elixir": 0, "dark_elixir": 0}

    gold_bbox = (65, 95, 200, 120)
    elixir_bbox = (65, 135, 200, 160)
    dark_bbox = (65, 175, 170, 200)

    gold_region = img[gold_bbox[1] : gold_bbox[3], gold_bbox[0] : gold_bbox[2]]
    elixir_region = img[
        elixir_bbox[1] : elixir_bbox[3], elixir_bbox[0] : elixir_bbox[2]
    ]
    dark_region = img[dark_bbox[1] : dark_bbox[3], dark_bbox[0] : dark_bbox[2]]

    gold_value = get_image_values(gold_region, "gold")
    elixir_value = get_image_values(elixir_region, "elixir")
    dark_value = get_image_values(dark_region, "dark_elixir")

    return {"gold": gold_value, "elixir": elixir_value, "dark_elixir": dark_value}


if __name__ == "__main__":
    result = get_resource_values("screen.png")
    print(result)
