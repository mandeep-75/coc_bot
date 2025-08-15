import cv2

# Load the image
img = cv2.imread('screen.png')
if img is None:
    raise FileNotFoundError('screen.png not found or failed to load')

# Example points to plot (x, y)
points = [
  (588, 272), (494, 395), (583, 205), (636, 395), (632, 500)
]

# Plot each point as a red circle
for (x, y) in points:
    cv2.circle(img, (x, y), radius=8, color=(0, 0, 255), thickness=-1)  # Red filled circle

# Save the result
cv2.imwrite('screen_with_points.png', img)
print('Plotted points and saved as screen_with_points.png')
