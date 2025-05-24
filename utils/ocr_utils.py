
## `utils/ocr_utils.py`

import cv2
import pytesseract

class OCRUtils:
    def __init__(self):
        # point to tesseract executable if needed
        pass

    def get_resources_from_screenshot(self, path: str) -> tuple[str,str,str]:
        img = cv2.imread(path)
        # Define boxes (x1,y1,x2,y2) same as in your original script
        boxes = {
            'gold': (95,95,220,120),
            'elixir': (95,135,220,160),
            'dark': (95,175,200,200)
        }
        res = []
        for key in ['gold','elixir','dark']:
            x1,y1,x2,y2 = boxes[key]
            region = img[y1:y2, x1:x2]
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            inv = cv2.bitwise_not(blur)
            txt = pytesseract.image_to_string(inv, config='--psm 7 -c tessedit_char_whitelist=0123456789')
            num = ''.join(c for c in txt if c.isdigit())
            res.append(num if num else '0')
        return tuple(res)
