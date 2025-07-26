import cv2

# Load image
image = cv2.imread('screen.png')

if image is None:
    raise FileNotFoundError("screen.png not found or failed to load")

# Define bounding boxes
boxes = {
    'Gold': (65, 95, 200, 120),
    'Elixir': (65, 135, 200, 160),
    'Dark Elixir': (65, 175, 150, 200),
    "trophies": (62, 231, 108, 254) 
}

# Draw rectangles and labels
for label, (x1, y1, x2, y2) in boxes.items():
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

# Save result
cv2.imwrite('screen_with_boxes.png', image)
print("Output saved as screen_with_boxes.png")
