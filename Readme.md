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
├── app.py                          # Flask entrypoint
│
├── database/
│   ├── model.py                    # SQLite schema and helpers
│   └── database.db                 # SQLite database (created at runtime)
│
├── detection/
│   ├── face_detector.py            # MTCNN-based detector
│   └── stream_processor.py         # Stream processing logic
│
├── static/
│   ├── images/
│   │   └── snapshot.jpg            # Saved detection images
│   ├── script.js                   # Frontend JavaScript
│   └── styles.css                  # Dashboard styling
│
├── templates/
│   ├── function/
│   │   ├── login.html              # Login screen template
│   │   └── index.html              # Dashboard template functions
│   └── venv/                       # Virtual environment files
│
├── config.py                       # Configuration settings             # Main SQLite database
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore file
└── README.md                       # This file
```

---

## 🧪 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/Praxxav/rtsp-face-detection.git
cd rtsp_face_detection
```

### 2. Create and activate virtual environment
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

### 4. Run the application
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

## 📊 Database Schema

The system uses SQLite with the following main tables:
- **Users**: Authentication and user management
- **Detections**: Face detection logs with timestamps and confidence scores
- **Alerts**: Alert management with viewed/dismissed status

---

## 🎯 Key Components

### Face Detection (`detection/`)
- `face_detector.py`: MTCNN-based face detection implementation
- `stream_processor.py`: Handles RTSP stream processing and frame analysis

### Database Layer (`database/`)
- `model.py`: SQLite schema definitions and database operations
- `database.db`: Runtime SQLite database file

### Web Interface (`static/` & `templates/`)
- Dashboard with real-time face detection statistics
- Login/authentication system
- Responsive design with CSS styling
- JavaScript for dynamic updates

---

## ⚠️ Notes

- This runs **only on CPU** with MTCNN
- Live streaming supports `rtsp://` URLs or defaults to webcam
- Performance: ~10–15 FPS on decent CPU
- Detection images are saved in `static/images/`
- Database is automatically created on first run

---

## 🔧 Configuration

Edit `config.py` to modify:
- RTSP stream URL
- Detection sensitivity
- Database settings
- Flask configuration

---

## 🐛 Troubleshooting

**Common Issues:**
1. **MTCNN Installation**: Ensure TensorFlow is properly installed
2. **Camera Access**: Check RTSP URL format and camera permissions
3. **Database Errors**: Ensure write permissions in project directory
4. **Port Conflicts**: Change Flask port in `app.py` if 5000 is occupied

---

## 👤 Developed By

**Pranav Kulkarni**  
For **Skylark Labs Assignment** – Test 2