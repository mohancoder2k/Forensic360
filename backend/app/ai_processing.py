import cv2
import numpy as np
from ultralytics import YOLO

# Load pre-trained YOLO model (download weights if needed)
model = YOLO("yolov8n.pt")  # Use 'yolov8n.pt' (Nano model) for speed

def detect_objects(image_path):
    """Detects objects in an image and returns bounding box details."""
    results = model(image_path)

    detections = []
    for result in results:
        for box in result.boxes.data.tolist():
            x1, y1, x2, y2, confidence, class_id = box
            detections.append({
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "confidence": round(confidence, 2),
                "class": model.names[int(class_id)]
            })
    
    return detections
