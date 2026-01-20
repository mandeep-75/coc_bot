import cv2
import numpy as np
import random

def get_static_deployment_points(img, num_points=30, scale_base=0.6):
    """
    Generates deployment points based on screen size, assuming the
    base occupies the central 'scale_base' fraction of the screen.
    Deploys in the area OUTSIDE this central zone (the margins).
    
    scale_base: 0.6 means central 60% is base. 20% margin on each side.
    """
    if img is None:
        return [] # Can't detect size
    
    h, w = img.shape[:2]
    
    # Define a central box for the base
    # cx, cy = w // 2, h // 2
    # box_w = int(w * scale_base)
    # box_h = int(h * scale_base)
    
    # Safe margins
    margin_x = int(w * (1 - scale_base) / 2)
    margin_y = int(h * (1 - scale_base) / 2)
    
    # Define limits for deployment (The outer frame)
    # x: [0, margin_x] AND [w-margin_x, w]
    # y: [0, margin_y] AND [h-margin_y, h]
    
    points = []
    
    # We want points *around* the base.
    # Top Strip (Full width)
    # points.extend([(random.randint(0, w), random.randint(0, margin_y)) for _ in range(num_points // 4)])
    
    # Actually, let's start with a simpler "Edge" approach
    # Just uniform random points in the safe border
    
    for _ in range(num_points):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            px = random.randint(0, w)
            py = random.randint(0, margin_y)
        elif side == 'bottom':
            px = random.randint(0, w)
            py = random.randint(h - margin_y, h)
        elif side == 'left':
            px = random.randint(0, margin_x)
            py = random.randint(0, h)
        elif side == 'right':
            px = random.randint(w - margin_x, w)
            py = random.randint(0, h)
            
        points.append((px, py))
        
    return points

# Keep original for compatibility if needed, or remove. 
# Re-adding the imports needed for compatibility / debugging
def get_valid_deployment_points(img, num_points=30, offset_outward=40):
    # Fallback to static if vision fails or requested
    return get_static_deployment_points(img, num_points, scale_base=0.7)
