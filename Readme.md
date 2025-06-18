# RTSP Face Detection System with Database and Alerts

A real-time face detection system that captures faces from RTSP streams, stores alerts in a SQLite database, and displays them on a browser-based dashboard.

---

## 🚀 Features

- 🔍 Real-time **MTCNN-based face detection**
- 🎥 RTSP/IP camera stream support (or webcam fallback)
- 📷 Snapshots with bounding boxes and keypoints
- 📊 Dashboard with total faces, FPS, uptime
- 🧠 SQLite-based logging of:
  - Detections (with confidence, image, bounding box)
  - Alerts (viewed/dismissed status)
- 👤 Simple Login/Logout authentication
- 📦 Modular structure for easy maintenance

---

## 🛠️ Technologies Used

- **Backend**: Python, Flask, OpenCV, MTCNN, SQLite
- **Frontend**: HTML, CSS, JS (vanilla)
- **Database**: SQLite3
- **Others**: Flask-SocketIO, bcrypt, threading, PIL

---

## 📁 Project Structure

```
rtsp_face_detection/
│
├── app.py                      # Flask entrypoint
├── templates/
│   ├── index.html              # Main dashboard UI
│   └── login.html              # Login screen
│
├── static/
│   ├── styles.css              # Dashboard styling
│   ├── script.js               # Frontend logic
│   └── images/                 # Saved detection images
│
├── detection/
│   ├── face_detector.py        # MTCNN-based detector
│   └── stream_processor.py     # Stream processing logic
│
├── database/
│   ├── model.py                # SQLite schema and helpers
│   └── database.db             # Created at runtime
│
└── README.md                   # This file
```

---

## 🧪 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/your-username/rtsp-face-detection.git
cd rtsp-face-detection
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate     # (Linux/macOS)
venv\Scripts\activate        # (Windows)
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> _If you get MTCNN errors, make sure TensorFlow and Pillow are installed correctly._

### 4. Run the app
```bash
python app.py
```

Open browser at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔐 Default Login

- **Username**: `admin`
- **Password**: `admin123`

> Auto-created on first run via `create_admin_user()`.

---

## ⚠️ Notes

- This runs **only on CPU** with MTCNN.
- Live streaming supports `rtsp://` or default to webcam.
- Performance ~10–15 FPS on decent CPU.

---

## 📌 TODOs

- [ ] Add WebSocket updates for real-time alerts
- [ ] Add admin panel to view users and control streams
- [ ] Containerize using Docker
- [ ] Export alerts to CSV


## 👤 Developed By

**Pranav Kulkarni**  
For **Skylark Labs Assignment** – Test 2
