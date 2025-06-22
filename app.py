import time

from flask import Flask, jsonify, render_template, request, session, redirect, url_for, send_from_directory, Response
from flask_socketio import SocketIO
import bcrypt, cv2, os
from datetime import datetime


from detection.face_detector import FaceDetector
from detection.optimized_stream_processor import OptimizedStreamProcessor

from database.model import init_db, get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'fsfidvkjfvkjk'
app.config['UPLOAD_FOLDER'] = 'static/images'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for performance optimization
face_detector = FaceDetector()
stream_processors = {}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Global stream processor
stream_processor = OptimizedStreamProcessor(0, app,socketio)  # 0 for webcam or RTSP URL

def create_admin_user():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
        if cursor.fetchone() is None:
            password = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (username, password_hash, last_login) VALUES (?, ?, ?)",
                ('admin', password, datetime.now())
            )
            conn.commit()
    finally:
        conn.close()

def ensure_detections_table():
    """Ensure the detections table exists - using existing init_db"""
    try:
        # Just call the existing init_db function to ensure tables exist
        init_db()
        print("Database tables verified/created successfully")
    except Exception as e:
        print(f"Error ensuring database tables: {e}")
        import traceback
        traceback.print_exc()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('function/login.html', error='Missing credentials')
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode(), user['password_hash']):
                session['user_id'] = user['id']
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('function/login.html', error='Invalid credentials')
        finally:
            conn.close()
    
    return render_template('function/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/video_feed')
def video_feed():
    """Optimized video feed that just streams frames"""
    def generate_frames():
        while True:
            if stream_processor.last_frame is not None:
                # Get the latest frame without blocking
                frame = stream_processor.last_frame.copy()
                
                # Encode frame efficiently
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]  # Reduce quality for speed
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                time.sleep(0.033)  # ~30 FPS for display

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/images/<filename>')
def serve_image(filename):
    """Serves image files from the UPLOAD_FOLDER."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('connect')
def on_connect():
    if 'user_id' not in session:
        return False
    print("Client connected:", session['username'])

@socketio.on('disconnect')
def on_disconnect():
    print("Client disconnected:", session.get('username'))

def alert_callback(data):
    """Emit alert to connected clients"""
    socketio.emit('new_alert', {
        **data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def api_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from database.model import get_detection_stats
        stats = get_detection_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/streams/start')
def start_stream():
    """Start the stream processing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        stream_processor.start()
        return jsonify({'status': 'started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/streams/stop')
def stop_stream():
    """Stop the stream processing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        stream_processor.stop()
        return jsonify({'status': 'stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def api_alerts():
    """Get recent alerts"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from database.model import get_recent_alerts
        limit = request.args.get('limit', 10, type=int)
        alerts = get_recent_alerts(limit=limit)
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    ensure_detections_table()  # Ensure proper table schema
    create_admin_user()
    
    # Start stream processing
    stream_processor.start()
    
    try:
        socketio.run(app, debug=False, allow_unsafe_werkzeug=True, host='0.0.0.0', port=5000)
    finally:
        stream_processor.stop()