import time
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, send_from_directory, Response
from flask_socketio import SocketIO, emit
import bcrypt, cv2, os, threading
from datetime import datetime


from detection.face_detector import FaceDetector
from detection.stream_processor import StreamProcessor
from database.model import init_db, get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'fsfidvkjfvkjk'
app.config['UPLOAD_FOLDER'] = 'static/images'
socketio = SocketIO(app, cors_allowed_origins="*")

face_detector = FaceDetector()
stream_processors = {}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
            return render_template('static/function/login.html', error='Missing credentials')
        
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
    
    return render_template('function/login.html')  # Corrected template path

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        cap = cv2.VideoCapture(0)  # replace with RTSP_URL
        frame_count = 0
        start_time = time.time()
        TARGET_FPS = 15
        FRAME_INTERVAL = 1.0 / TARGET_FPS

        while True:
            loop_start = time.time()
            success, frame = cap.read()
            if not success:
                continue

            # Detection
            detections = face_detector.detect_optimized(frame, 0.8)
            if detections:
                for det in detections:
                    x, y, w, h = det['box']
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Save snapshot
                snapshot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'snapshot.jpg')
                cv2.imwrite(snapshot_path, frame)

                # Emit detection alert
                alert_callback({
                    'face_count': len(detections),
                    'stream': 'webcam',
                    'frame_url': '/images/snapshot.jpg'
                })

            # FPS tracking
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                fps = frame_count / elapsed
                socketio.emit('fps_update', {'fps': round(fps, 2)})
                frame_count = 0
                start_time = time.time()

            # Encode and stream frame for browser
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

            # --- Add this block to limit FPS ---
            loop_end = time.time()
            process_time = loop_end - loop_start
            if process_time < FRAME_INTERVAL:
                time.sleep(FRAME_INTERVAL - process_time)
            # -----------------------------------

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
    socketio.emit('new_alert', {
        **data,
        'timestamp': datetime.now().isoformat()
    })
    

@app.route('/api/stats')
def api_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from database.model import get_detection_stats  # Import inside function
    stats = get_detection_stats()
    return jsonify(stats)

if __name__ == '__main__':
    init_db()
    create_admin_user()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)