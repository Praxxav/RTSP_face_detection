import cv2, threading, time
from mtcnn import MTCNN

class FaceDetector:
    def __init__(self):
        self.detector = MTCNN()
        self.lock = threading.Lock()

    def detect_optimized(self, frame, threshold=0.8):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with self.lock:
            results = self.detector.detect_faces(rgb)
        return [r for r in results if r['confidence'] >= threshold]
