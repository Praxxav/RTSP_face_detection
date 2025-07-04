# detection/vehicle_detector.py
from ultralytics import YOLO
import cv2

class VehicleDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.allowed_classes = {"car", "truck", "bus", "motorbike", "bicycle"}

    def detect_vehicles(self, frame):
        results = self.model(frame)[0]
        detections = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            if label in self.allowed_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                detections.append({
                    "box": [x1, y1, x2 - x1, y2 - y1],
                    "label": label,
                    "confidence": confidence
                })

        return detections
