import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'database/database.db'

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """Initialize database with required tables"""
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Streams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rtsp_url TEXT NOT NULL,
            description TEXT,
            detection_enabled BOOLEAN DEFAULT 1,
            confidence_threshold REAL DEFAULT 0.8,
            last_connection TIMESTAMP,
            status TEXT DEFAULT 'disconnected',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Detections table
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
            FOREIGN KEY (stream_id) REFERENCES streams (id) ON DELETE CASCADE
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_id INTEGER NOT NULL,
            viewed BOOLEAN DEFAULT 0,
            dismissed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            viewed_at TIMESTAMP,
            FOREIGN KEY (detection_id) REFERENCES detections (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_detections_stream_id ON detections(stream_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_detections_created_at ON detections(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_detection_id ON alerts(detection_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_viewed ON alerts(viewed)')
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully")

def update_stream_status(stream_id, status, last_connection=None):
    """Update stream connection status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if last_connection is None:
        last_connection = datetime.now()
    
    cursor.execute(
        "UPDATE streams SET status = ?, last_connection = ? WHERE id = ?",
        (status, last_connection, stream_id)
    )
    conn.commit()
    conn.close()

def get_stream_config(stream_id):
    """Get stream configuration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM streams WHERE id = ?", (stream_id,))
    stream = cursor.fetchone()
    conn.close()
    return dict(stream) if stream else None

def save_detection(stream_id, confidence_score, image_path, bbox=None):
    """Save face detection result"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    bbox_x = bbox[0] if bbox else None
    bbox_y = bbox[1] if bbox else None
    bbox_width = bbox[2] if bbox else None
    bbox_height = bbox[3] if bbox else None
    
    cursor.execute("""
        INSERT INTO detections (stream_id, confidence_score, image_path, 
                              bbox_x, bbox_y, bbox_width, bbox_height, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (stream_id, confidence_score, image_path, 
          bbox_x, bbox_y, bbox_width, bbox_height, datetime.now()))
    
    detection_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return detection_id

def create_alert(detection_id):
    """Create alert for detection"""
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

def get_recent_alerts(limit=10, stream_id=None):
    """Get recent alerts with detection and stream info"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT a.*, s.name as stream_name, d.confidence_score, d.image_path,
               d.bbox_x, d.bbox_y, d.bbox_width, d.bbox_height
        FROM alerts a
        JOIN detections d ON a.detection_id = d.id
        JOIN streams s ON d.stream_id = s.id
    """
    params = []
    
    if stream_id:
        query += " WHERE s.id = ?"
        params.append(stream_id)
    
    query += " ORDER BY a.created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    alerts = cursor.fetchall()
    conn.close()
    
    return [dict(alert) for alert in alerts]

def get_detection_stats(stream_id=None, days=7):
    """Get detection statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    base_query = """
        FROM detections d
        JOIN streams s ON d.stream_id = s.id
        WHERE d.created_at >= datetime('now', '-{} days')
    """.format(days)
    
    params = []
    if stream_id:
        base_query += " AND s.id = ?"
        params.append(stream_id)
    
    # Total detections
    cursor.execute(f"SELECT COUNT(*) as count {base_query}", params)
    total_detections = cursor.fetchone()['count']
    
    # Average confidence
    cursor.execute(f"SELECT AVG(confidence_score) as avg_conf {base_query}", params)
    avg_confidence = cursor.fetchone()['avg_conf'] or 0
    
    # Detections by day
    cursor.execute(f"""
        SELECT DATE(d.created_at) as date, COUNT(*) as count 
        {base_query}
        GROUP BY DATE(d.created_at)
        ORDER BY date DESC
    """, params)
    daily_stats = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_detections': total_detections,
        'avg_confidence': round(avg_confidence, 3),
        'daily_stats': [dict(stat) for stat in daily_stats]
    }

def cleanup_old_data(days=30):
    """Clean up old detection data and images"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get old detection image paths before deletion
    cursor.execute("""
        SELECT image_path FROM detections 
        WHERE created_at < datetime('now', '-{} days')
        AND image_path IS NOT NULL
    """.format(days))
    old_images = cursor.fetchall()
    
    # Delete old records (cascade will handle alerts)
    cursor.execute("""
        DELETE FROM detections 
        WHERE created_at < datetime('now', '-{} days')
    """.format(days))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    # Clean up old image files
    for image in old_images:
        try:
            if image['image_path'] and os.path.exists(image['image_path']):
                os.remove(image['image_path'])
        except Exception as e:
            print(f"Error deleting image {image['image_path']}: {e}")
    
    return deleted_count

if __name__ == "__main__":
    init_db()
    print("Database setup complete")