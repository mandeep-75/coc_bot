import cv2
import os
import logging
from datetime import datetime

class DebugVisualizer:
    def __init__(self, output_dir: str = ".", debug_mode: bool = True):
        self.output_dir = output_dir
        self.current_screenshot = None
        self.current_visualization = None
        self.debug_mode = debug_mode
    
    def load_screenshot(self, screenshot_path: str) -> bool:
        if not self.debug_mode:
            return True
            
        try:
            self.current_screenshot = cv2.imread(screenshot_path)
            if self.current_screenshot is not None:
                self.current_visualization = self.current_screenshot.copy()
                return True
            return False
        except Exception as e:
            logging.error(f"Error loading screenshot: {e}")
            return False
    
    def draw_detection(self, position: tuple, size: tuple, label: str, color: tuple = (0, 255, 0)) -> None:
        if not self.debug_mode or self.current_visualization is None:
            return
            
        x, y = position
        width, height = size
        cv2.rectangle(self.current_visualization, (x, y), (x + width, y + height), color, 2)
        cv2.putText(self.current_visualization, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def draw_resource_info(self, bbox: tuple, value: int, threshold: int, label: str, text_offset_x: int, text_offset_y: int) -> None:
        if not self.debug_mode or self.current_visualization is None:
            return
            
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        meets = value >= threshold
        
        self.draw_detection(
            (x1, y1),
            (width, height),
            "",
            color=(0, 255, 0) if meets else (0, 0, 255)
        )
        
        cv2.putText(
            self.current_visualization,
            f"{label}: {value:,} {'✓' if meets else '✗'}",
            (text_offset_x, y1 + text_offset_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0) if meets else (0, 0, 255),
            2
        )
    
    def draw_button_detection(self, position: tuple, size: tuple, label: str, confidence: float) -> None:
        if not self.debug_mode or self.current_visualization is None:
            return
            
        x, y = position
        width, height = size
        
        self.draw_detection(
            position,
            size,
            f"{label} ({confidence:.1f}%)",
            color=(0, 255, 255)
        )
        
        center_x = x + width // 2
        center_y = y + height // 2
        
        cv2.circle(
            self.current_visualization,
            (center_x, center_y),
            5,
            (0, 0, 255),
            -1
        )
    
    def draw_decision(self, text_offset_x: int, resources_met: int, meets: bool, decision: str) -> None:
        if not self.debug_mode or self.current_visualization is None:
            return
            
        cv2.putText(
            self.current_visualization,
            f"Criteria: {resources_met}/3 thresholds met (need 2+)",
            (text_offset_x, self.current_visualization.shape[0] - 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255) if not meets else (0, 255, 0),
            1
        )
        
        self.current_visualization = cv2.putText(
            self.current_visualization,
            decision,
            (text_offset_x, self.current_visualization.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0) if meets else (0, 0, 255),
            4
        )
    
    def draw_thresholds(self, text_offset_x: int, gold_threshold: int, elixir_threshold: int, dark_threshold: int) -> None:
        if not self.debug_mode or self.current_visualization is None:
            return
            
        cv2.putText(
            self.current_visualization,
            f"Thresholds - G:{gold_threshold} E:{elixir_threshold} D:{dark_threshold}",
            (text_offset_x, self.current_visualization.shape[0] - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )
    
    def draw_troop_detection(self, position: tuple, size: tuple, element_name: str, confidence: float, count: int) -> None:
        if not self.debug_mode or self.current_visualization is None:
            return
            
        x, y = position
        width, height = size
        
        self.draw_detection(
            position,
            size,
            f"{element_name} ({confidence:.2f}) x{count}",
            color=(0, 255, 0)
        )
    
    def draw_deployment_region(self, y_start: int, image_width: int, image_height: int) -> None:
        if not self.debug_mode or self.current_visualization is None:
            return
            
        cv2.rectangle(
            self.current_visualization,
            (0, y_start),
            (image_width, image_height),
            (0, 255, 0),
            2
        )
    
    def save_visualization(self, filename: str = "result.png") -> bool:
        if not self.debug_mode or self.current_visualization is None:
            return True
            
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(
                self.current_visualization,
                timestamp,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, filename)
            cv2.imwrite(output_path, self.current_visualization)
            return True
        except Exception as e:
            logging.error(f"Error saving visualization: {e}")
            return False 