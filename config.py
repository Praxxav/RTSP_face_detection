
import cv2
import os

class Config:
    # RTSP Stream Configuration
    rtspUrl = "rtsp://admin:admin123@49.248.155.178:555/cam/realmonitor?channel=1&subtype=0"
    
    
    # RTSP_URL = "rtsp://username:password@ip:port/live"
    # RTSP_URL = "rtsp://192.168.1.100:8080/video/mjpeg"
  
    
    # Face Detection Models (OpenCV Haar Cascades)
    CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    
    # Detection Parameters
    SCALE_FACTOR = 1.1
    MIN_NEIGHBORS = 5
    MIN_SIZE = (30, 30)
    MAX_SIZE = (300, 300)
    
    # Frame Processing
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS_LIMIT = 15
    
    # Detection Settings
    CONFIDENCE_THRESHOLD = 0.5
    DETECTION_COOLDOWN = 1.0  # seconds between detections
    
    # Output Settings
    SAVE_DETECTIONS = True
    OUTPUT_DIR = "detections"
    SAVE_FORMAT = "jpg"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "face_detection.log"
    
    # Web Interface
    WEB_PORT = 5000
    WEB_HOST = "0.0.0.0"
    
    # Alert Settings
    ENABLE_ALERTS = True
    MAX_FACES_ALERT = 2
    
    # Performance
    SKIP_FRAMES = 2  # Process every nth frame
    RESIZE_FRAME = True
    
    @staticmethod
    def create_directories():
        """Create necessary directories"""
        if Config.SAVE_DETECTIONS and not os.path.exists(Config.OUTPUT_DIR):
            os.makedirs(Config.OUTPUT_DIR)
    
    @staticmethod
    def validate_rtsp_url():
        """Basic RTSP URL validation"""
        url = Config.RTSP_URL
        if isinstance(url, int):  # Webcam index
            return True
        if not str(url).startswith('rtsp://'):
            raise ValueError("Invalid RTSP URL format")
        return True