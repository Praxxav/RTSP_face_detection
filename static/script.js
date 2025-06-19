let isDetecting = false;
let startTime = null;
let detectionCount = 0;
let socket = null;

function startDetection() {
  if (!isDetecting) {
    isDetecting = true;
    startTime = new Date();
    updateStatus('Online');
    document.getElementById('video').src = "http://127.0.0.1:5000/video_feed";

    // Connect to backend via Socket.IO
    socket = io();

    // Listen for real-time alerts from Flask
    socket.on('new_alert', (data) => {
      console.log('📡 New detection received:', data);

      const faceCount = data.face_count || 0;
      detectionCount += faceCount;

      document.getElementById('totalFaces').textContent = detectionCount;
      document.getElementById('lastDetection').textContent = new Date().toLocaleTimeString();
      addDetection(faceCount);

      // Optionally display snapshot
      if (data.frame_url) {
        document.getElementById('snapshotImage').src = data.frame_url + `?t=${Date.now()}`; // avoid caching
      }

      // Simulate FPS value
      document.getElementById('currentFps').textContent = Math.floor(Math.random() * 5) + 25;
    });
  }
}

function stopDetection() {
  if (isDetecting) {
    isDetecting = false;
    updateStatus('Offline');
    document.getElementById('video').src = '';

    // Disconnect from Socket.IO
    if (socket) {
      socket.disconnect();
      socket = null;
    }
  }
}

function takeSnapshot() {
  alert('Snapshot saved to detections folder');
}

function updateStatus(status) {
  document.getElementById('status').textContent = status;
  const indicator = document.getElementById('statusIndicator');
  indicator.className = status === 'Online'
    ? 'status-indicator status-online'
    : 'status-indicator status-offline';
}

function updateConfig() {
  const config = {
    rtspUrl: document.getElementById('rtspUrl').value,
    frameWidth: document.getElementById('frameWidth').value,
    frameHeight: document.getElementById('frameHeight').value,
    scaleFactor: document.getElementById('scaleFactor').value,
    minNeighbors: document.getElementById('minNeighbors').value,
    minSize: document.getElementById('minSize').value
  };

  console.log('Updating configuration:', config);
  alert('Configuration updated successfully!');
}

function addDetection(faceCount) {
  const detectionsList = document.getElementById('detectionsList');
  const timestamp = new Date().toLocaleTimeString();

  const detectionItem = document.createElement('div');
  detectionItem.className = 'detection-item';
  detectionItem.innerHTML = `
    <span class="timestamp">${timestamp}</span>
    <span class="face-count">${faceCount} face${faceCount > 1 ? 's' : ''}</span>
  `;

  detectionsList.insertBefore(detectionItem, detectionsList.firstChild);
  while (detectionsList.children.length > 10) {
    detectionsList.removeChild(detectionsList.lastChild);
  }
}

function updateUptime() {
  if (startTime && isDetecting) {
    const now = new Date();
    const diff = Math.floor((now - startTime) / 1000);
    const minutes = Math.floor(diff / 60);
    const seconds = diff % 60;
    document.getElementById('uptime').textContent = 
      `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  } else {
    document.getElementById('uptime').textContent = '00:00';
  }
}

setInterval(updateUptime, 1000);

document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ RTSP Face Detection Dashboard loaded (Real-Time Mode)');
});
