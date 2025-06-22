import cv2
import time
import os
from datetime import datetime
import threading
import queue
import numpy as np

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
        self.daemon = True  # Dies when main thread dies
        
        # Performance optimization variables
        self.target_fps = 15
        self.frame_skip = 2  # Process every 2nd frame for detection
        self.frame_count = 0
        self.last_frame = None
        
        # Threading for async operations
        self.detection_queue = queue.Queue(maxsize=5)
        self.detection_thread = threading.Thread(target=self._detection_worker, daemon=True)
        self.save_thread = threading.Thread(target=self._save_worker, daemon=True)
        self.save_queue = queue.Queue(maxsize=10)
        
        # FPS tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        
    def run(self):
        """Main capture loop - optimized for 15 FPS"""
        cap = self._setup_capture()
        if not cap:
            return
            
        # Start worker threads
        self.detection_thread.start()
        self.save_thread.start()
        
        frame_time = 1.0 / self.target_fps
        
        try:
            while self.running and cap.isOpened():
                loop_start = time.time()
                
                ret, frame = cap.read()
                if not ret:
                    print(f"Stream {self.stream_id}: Failed to read frame")
                    time.sleep(0.1)
                    continue
                
                # Optimize frame size for better performance
                frame = self._optimize_frame(frame)
                self.last_frame = frame.copy()
                
                # Skip frames for detection to maintain FPS
                self.frame_count += 1
                if self.frame_count % self.frame_skip == 0:
                    try:
                        # Non-blocking detection queue
                        self.detection_queue.put_nowait({
                            'frame': frame.copy(),
                            'timestamp': time.time()
                        })
                    except queue.Full:
                        # Skip this detection if queue is full
                        pass
                
                # FPS tracking and reporting
                self._update_fps_counter()
                
                # Maintain target FPS
                elapsed = time.time() - loop_start
                sleep_time = frame_time - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except Exception as e:
            print(f"Stream {self.stream_id} error: {e}")
        finally:
            cap.release()
            self.running = False
    
    def _setup_capture(self):
        """Setup video capture with optimized settings"""
        cap = cv2.VideoCapture(self.rtsp_url)
        
        if not cap.isOpened():
            print(f"Failed to open stream: {self.rtsp_url}")
            return None
        
        # Optimize capture settings
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer lag
        cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        # Try to set codec for better performance
        try:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        except:
            pass
        
        return cap
    
    def _optimize_frame(self, frame):
        """Resize frame if too large for better performance"""
        height, width = frame.shape[:2]
        
        # Resize if width > 640 for better performance
        if width > 640:
            scale = 640 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        return frame
    
    def _detection_worker(self):
        """Worker thread for face detection"""
        while self.running:
            try:
                data = self.detection_queue.get(timeout=1.0)
                frame = data['frame']
                timestamp = data['timestamp']
                
                # Perform face detection
                detections = self.face_detector.detect_optimized(frame, self.confidence_threshold)
                
                if detections:
                    current_time = time.time()
                    
                    # Check cooldown period
                    if current_time - self.last_alert_time > self.cooldown:
                        self.last_alert_time = current_time
                        
                        # Draw bounding boxes on frame
                        annotated_frame = self._draw_detections(frame, detections)
                        
                        # Queue for async saving
                        try:
                            self.save_queue.put_nowait({
                                'frame': annotated_frame,
                                'detections': detections,
                                'timestamp': datetime.now()
                            })
                        except queue.Full:
                            print(f"Stream {self.stream_id}: Save queue full, skipping save")
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Stream {self.stream_id} detection error: {e}")
    
    def _save_worker(self):
        """Worker thread for saving snapshots"""
        while self.running:
            try:
                data = self.save_queue.get(timeout=1.0)
                frame = data['frame']
                detections = data['detections']
                timestamp = data['timestamp']
                
                # Save snapshot
                filename = f"stream{self.stream_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join("static", "images", filename)  # Fixed path
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Save with compression for faster I/O
                cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                # Trigger alert callback
                max_confidence = max([d['confidence'] for d in detections])
                self.alert_callback({
                    "stream_id": self.stream_id,
                    "confidence_score": max_confidence,
                    "image_path": filename,
                    "face_count": len(detections),
                    "timestamp": timestamp.isoformat()
                })
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Stream {self.stream_id} save error: {e}")
    
    def _draw_detections(self, frame, detections):
        """Draw bounding boxes on detected faces"""
        annotated_frame = frame.copy()
        
        for detection in detections:
            x, y, w, h = detection['box']
            confidence = detection['confidence']
            
            # Draw rectangle
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw confidence score
            label = f"{confidence:.2f}"
            cv2.putText(annotated_frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return annotated_frame
    
    def _update_fps_counter(self):
        """Track and report FPS"""
        self.fps_counter += 1
        elapsed = time.time() - self.fps_start_time
        
        if elapsed >= 1.0:
            actual_fps = self.fps_counter / elapsed
            print(f"Stream {self.stream_id} FPS: {actual_fps:.1f} | Detections in queue: {self.detection_queue.qsize()}")
            
            self.fps_counter = 0
            self.fps_start_time = time.time()
    
    def get_latest_frame(self):
        """Get the latest frame for streaming"""
        return self.last_frame
    
    def get_stats(self):
        """Get stream statistics"""
        return {
            'stream_id': self.stream_id,
            'running': self.running,
            'detection_queue_size': self.detection_queue.qsize(),
            'save_queue_size': self.save_queue.qsize(),
            'last_alert_time': self.last_alert_time
        }
    
    def stop(self):
        """Stop the stream processor"""
        print(f"Stopping stream {self.stream_id}")
        self.running = False
        
        # Wait for threads to finish
        if self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2)
        if self.save_thread.is_alive():
            self.save_thread.join(timeout=2)


# Example usage:
if __name__ == "__main__":
    # Mock face detector for testing
    class MockFaceDetector:
        def detect_optimized(self, frame, threshold):
            # Mock detection - replace with your actual detector
            return [{'box': (100, 100, 50, 50), 'confidence': 0.95}]
    
    # Mock alert callback
    def alert_callback(data):
        print(f"Alert: {data}")
    
    # Test the processor
    processor = StreamProcessor(
        stream_id=1,
        rtsp_url=0,  # Use webcam for testing
        confidence_threshold=0.8,
        face_detector=MockFaceDetector(),
        alert_callback=alert_callback
    )
    
    processor.start()
    
    try:
        time.sleep(30)  # Run for 30 seconds
    except KeyboardInterrupt:
        pass
    finally:
        processor.stop()