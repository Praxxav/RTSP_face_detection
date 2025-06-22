import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'database/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """Create required tables if they don't exist"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rtsp_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stream_id INTEGER NOT NULL,
            confidence_score REAL NOT NULL,
            image_path TEXT,
            bbox_x INTEGER,
            bbox_y INTEGER,
            bbox_width INTEGER,
            bbox_height INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stream_id) REFERENCES streams(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_id INTEGER NOT NULL,
            viewed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (detection_id) REFERENCES detections(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
   

def save_detection(stream_id, confidence_score, image_path, bbox=None):
    """Insert a detection into the detections table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    bbox_x, bbox_y, bbox_w, bbox_h = (bbox if bbox else (None,)*4)

    cursor.execute("""
        INSERT INTO detections (stream_id, confidence_score, image_path, 
            bbox_x, bbox_y, bbox_width, bbox_height, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (stream_id, confidence_score, image_path, 
          bbox_x, bbox_y, bbox_w, bbox_h, datetime.now()))

    detection_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return detection_id

def create_alert(detection_id):
    """Insert an alert into the alerts table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (detection_id, created_at, viewed)
        VALUES (?, ?, 0)
    """, (detection_id, datetime.now()))

    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alert_id

if __name__ == "__main__":
    init_db()
