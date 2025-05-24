
## `utils/main_utils.py`

import time

def click_button(adb, image, folder: str, name: str) -> bool:
    return image.find_and_click_image(adb, folder, name)


def wait_for_ui_stabilization(seconds: float):
    time.sleep(seconds)
