import cv2, time, os
from datetime import datetime
import threading

class StreamProcessor(threading.Thread):
    def __init__(self, stream_id, rtsp_url, confidence_threshold, face_detector, alert_callback, cooldown=30):
        super().__init__()
        self.stream_id = stream_id
        self.rtsp_url = rtsp_url
        self.confidence_threshold = confidence_threshold
        self.face_detector = face_detector
        self.alert_callback = alert_callback
        self.cooldown = cooldown
        self.last_alert_time = 0
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        while self.running and cap.isOpened():
            start = time.time()
            ret, frame = cap.read()
            if not ret:
                continue
            detections = self.face_detector.detect_optimized(frame, self.confidence_threshold)
            if detections and time.time() - self.last_alert_time > self.cooldown:
                self.last_alert_time = time.time()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"stream{self.stream_id}_{timestamp}.jpg"
                filepath = os.path.join("static", "images", filename)
                cv2.imwrite(filepath, frame)
                self.alert_callback({
                    "stream_id": self.stream_id,
                    "confidence_score": detections[0]['confidence'],
                    "image_path": filename
                })
            time.sleep(max(0, (1 / 15) - (time.time() - start)))
        cap.release()

    def stop(self):
        self.running = False
