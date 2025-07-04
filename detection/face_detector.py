
import cv2, threading
from mtcnn import MTCNN
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class FaceDetector:
    def __init__(self):
        self.detector = MTCNN()
        self.lock = threading.Lock()
        

    def detect_optimized(self, frame, threshold=0.8):
        if frame is None or not hasattr(frame, "shape"):
            return []
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with self.lock:
            results = self.detector.detect_faces(rgb)
        return [r for r in results if r['confidence'] >= threshold]

