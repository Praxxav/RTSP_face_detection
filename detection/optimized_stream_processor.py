
import time
import threading
import queue
import os
from datetime import datetime
import cv2
from flask_socketio import SocketIO

from detection.face_detector import FaceDetector
from database.model import save_detection, create_alert
 
class OptimizedStreamProcessor:
    def __init__(self, stream_url, app,socketio,confidence_threshold=0.8):
        self.stream_url = stream_url
        self.confidence_threshold = confidence_threshold
        self.cap = None
        self.running = False
        self.last_frame = None
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.target_fps = 15
        self.frame_skip = 2
        self.frame_count = 0
        self.frame_queue = queue.Queue(maxsize=10)

        self.face_detector = FaceDetector()
        self.last_detection_time = {}
        self.alert_cooldown = 30
        self.upload_folder = app.config['UPLOAD_FOLDER']
        self.app = app
        self.socketio = socketio
  
    def start(self):
        self.running = True
        self.cap = cv2.VideoCapture(self.stream_url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        threading.Thread(target=self._capture_frames, daemon=True).start()
        threading.Thread(target=self._process_detections, daemon=True).start()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def _capture_frames(self):
        frame_time = 1.0 / self.target_fps

        while self.running:
            start_time = time.time()
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            height, width = frame.shape[:2]
            if width > 640:
                scale = 640 / width
                frame = cv2.resize(frame, (int(width * scale), int(height * scale)))

            self.last_frame = frame.copy()

            self.frame_count += 1
            if self.frame_count % self.frame_skip == 0:
                try:
                    self.frame_queue.put_nowait((frame.copy(), time.time()))
                except queue.Full:
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait((frame.copy(), time.time()))
                    except queue.Empty:
                        pass

            self.fps_counter += 1
            elapsed = time.time() - self.fps_start_time
            if elapsed >= 1.0:
                actual_fps = self.fps_counter / elapsed
                print(f"Actual FPS: {actual_fps:.1f}")
                self.socketio.emit('fps_update', {'fps': round(actual_fps, 1),
                                                  })
                self.fps_counter = 0
                self.fps_start_time = time.time()

            elapsed_frame_time = time.time() - start_time
            sleep_time = frame_time - elapsed_frame_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _process_detections(self):
        while self.running:
            try:
                frame, timestamp = self.frame_queue.get(timeout=1.0)
                detections = self.face_detector.detect_optimized(frame, self.confidence_threshold)
                print(f"🧪 Detections: {detections}")

                self.socketio.emit('face_count_update', {
                'face_count': len(detections),
                'stream': 'webcam',
                'timestamp': datetime.now().isoformat()
})
                if detections:
                    current_time = datetime.now()
                    stream_id = 'webcam'

                    if (stream_id not in self.last_detection_time or
                            (current_time - self.last_detection_time[stream_id]).seconds >= self.alert_cooldown):

                        annotated_frame = frame.copy()
                        for det in detections:
                            x, y, w, h = det['box']
                            confidence = det['confidence']
                            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(annotated_frame, f'{confidence:.2f}', (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                        threading.Thread(target=self._save_snapshot_async,
                                         args=(annotated_frame, current_time, detections), daemon=True).start()

                        self.last_detection_time[stream_id] = current_time
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Detection error: {e}")

    def _save_snapshot_async(self, frame, timestamp, detections):
        try:
            filename = f"detection_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
            snapshot_path = os.path.join(self.upload_folder, filename)
            cv2.imwrite(snapshot_path, frame)

            for detection in detections:
                x, y, w, h = detection['box']
                bbox = (x, y, w, h)
                detection_id = save_detection(stream_id=1, confidence_score=detection['confidence'],
                                              image_path=filename, bbox=bbox)
                alert_id = create_alert(detection_id)

            self.socketio.emit('new_alert', {
                'face_count': len(detections),
                'stream': 'webcam',
                'frame_url': f'/images/{filename}',
                'confidence': max([d['confidence'] for d in detections]),
                'timestamp': timestamp.isoformat()
            })

        except Exception as e:
            print(f"Snapshot save error: {e}")