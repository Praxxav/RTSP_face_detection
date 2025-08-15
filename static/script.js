let isDetecting = false;
let startTime = null;
let detectionCount = 0;
let socket = null;
let animationFrameId = null;

// Initialize AOS animations
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Check if AOS is available
        if (typeof AOS !== 'undefined') {
            try {
                AOS.init({
                    duration: 800,
                    easing: 'ease-out-cubic',
                    once: true,
                    offset: 100
                });
                console.log('AOS animations initialized');
            } catch (aosError) {
                console.warn('AOS initialization failed:', aosError);
            }
        } else {
            console.log('AOS library not available, skipping animations');
        }
        
        console.log('🚀 RTSP Detection Hub loaded with enhanced UI');
        initializeUI();
        
        // Make sure all functions are available globally
        window.startDetection = startDetection;
        window.stopDetection = stopDetection;
        window.takeSnapshot = takeSnapshot;
        window.logout = logout;
        window.updateConfig = updateConfig;
        
        console.log('All functions registered globally');
        
    } catch (error) {
        console.error('Error initializing UI:', error);
    }
});

function initializeUI() {
    // Add smooth entrance animations
    document.querySelectorAll('section').forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            section.style.transition = 'all 0.6s ease-out';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 200);
    });
    
    // Initialize status
    updateStatus('Offline');
    
    // Add hover effects to stat cards
    document.querySelectorAll('.stat-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function startDetection() {
    if (!isDetecting) {
        isDetecting = true;
        startTime = new Date();
        updateStatus('Online');
        
        // Update button states - check if elements exist first
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const video = document.getElementById('video');
        
        if (startBtn) startBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'flex';
        
        // Start video stream
        if (video) video.src = "/video_feed";
        
        // Hide video overlay
        const overlay = document.querySelector('.video-overlay');
        if (overlay) overlay.style.display = 'none';
        
        // Initialize socket connection
        try {
            socket = io();
            
            socket.on('connect', () => {
                console.log('Socket.IO connected successfully');
            });
            
            socket.on('connect_error', (error) => {
                console.warn('Socket.IO connection error:', error);
                showNotification('Connection error - some features may not work', 'warning');
            });
            
            socket.on('fps_update', (data) => {
                animateNumberChange('currentFps', Math.round(data.fps));
            });

            socket.on('new_alert', (data) => {
                console.log('📡 New detection received:', data);
                handleNewDetection(data);
            });

            socket.on('face_count_update', (data) => {
                animateNumberChange('totalFaces', data.face_count);
            });
            
        } catch (socketError) {
            console.error('Failed to initialize Socket.IO:', socketError);
            showNotification('Failed to establish real-time connection', 'error');
        }
        
        // Add success animation
        showNotification('Detection started successfully!', 'success');
        
        // Start uptime counter
        startUptimeCounter();
    }
}

function stopDetection() {
    if (isDetecting) {
        isDetecting = false;
        updateStatus('Offline');
        
        // Update button states - check if elements exist first
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const video = document.getElementById('video');
        
        if (startBtn) startBtn.style.display = 'flex';
        if (stopBtn) stopBtn.style.display = 'none';
        
        // Stop video stream
        if (video) video.src = '';
        
        // Show video overlay
        const overlay = document.querySelector('.video-overlay');
        if (overlay) overlay.style.display = 'flex';
        
        // Disconnect socket
        if (socket) {
            socket.disconnect();
            socket = null;
        }
        
        // Stop uptime counter
        stopUptimeCounter();
        
        // Add info animation
        showNotification('Detection stopped', 'info');
    }
}

function handleNewDetection(data) {
    const faceCount = data.face_count || 0;
    detectionCount += faceCount;

    // Animate number changes
    animateNumberChange('totalFaces', detectionCount);
    document.getElementById('lastDetection').textContent = new Date(data.timestamp).toLocaleTimeString();

    // Add to recent list with animation
    addDetection(faceCount, data.frame_url);

    // Show snapshot if available - using the modal instead
    if (data.frame_url) {
        showSnapshotModal(data.frame_url);
    }
    
    // Update detection count badge
    updateDetectionCount();
    
    // Add success notification
    showNotification(`${faceCount} detection${faceCount !== 1 ? 's' : ''} found!`, 'success');
}

function takeSnapshot() {
    if (isDetecting) {
        // Simulate snapshot capture
        const video = document.getElementById('video');
        if (video.src) {
            // Create a canvas to capture the current frame
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            
            // Draw the video frame to canvas
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert to data URL and show in modal
            const snapshotUrl = canvas.toDataURL('image/jpeg');
            showSnapshotModal(snapshotUrl);
            
            showNotification('Snapshot captured successfully!', 'success');
        } else {
            showNotification('No video stream available', 'warning');
        }
    } else {
        showNotification('Please start detection first', 'warning');
    }
}

function showSnapshotModal(imageUrl) {
    const modal = document.getElementById('snapshotModal');
    const image = document.getElementById('snapshotImage');
    
    image.src = imageUrl;
    modal.classList.add('active');
    
    // Add entrance animation
    modal.style.opacity = '0';
    modal.style.transform = 'scale(0.9)';
    
    setTimeout(() => {
        modal.style.transition = 'all 0.3s ease-out';
        modal.style.opacity = '1';
        modal.style.transform = 'scale(1)';
    }, 10);
}

function closeSnapshotModal() {
    const modal = document.getElementById('snapshotModal');
    
    modal.style.transition = 'all 0.3s ease-in';
    modal.style.opacity = '0';
    modal.style.transform = 'scale(0.9)';
    
    setTimeout(() => {
        modal.classList.remove('active');
    }, 300);
}

function updateStatus(status) {
    const statusText = document.getElementById('statusText');
    const statusDot = document.getElementById('statusDot');
    const statusBadge = document.getElementById('statusBadge');
    
    // Check if elements exist before proceeding
    if (!statusText || !statusDot || !statusBadge) {
        console.warn('Status elements not found');
        return;
    }
    
    statusText.textContent = status;
    
    if (status === 'Online') {
        statusDot.classList.add('online');
        statusBadge.style.borderColor = 'var(--success)';
        statusBadge.style.background = 'rgba(78, 205, 196, 0.1)';
    } else {
        statusDot.classList.remove('online');
        statusBadge.style.borderColor = 'var(--card-border)';
        statusBadge.style.background = 'rgba(255, 255, 255, 0.1)';
    }
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
    
    // Add save animation
    const saveBtn = document.querySelector('.config-save-btn');
    saveBtn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Saved!';
    saveBtn.style.background = 'var(--success)';
    
    setTimeout(() => {
        saveBtn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 7H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 11H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 15H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Save Config';
        saveBtn.style.background = 'var(--success)';
    }, 2000);
    
    showNotification('Configuration updated successfully!', 'success');
}

function addDetection(faceCount, frameUrl = null) {
    const detectionsList = document.getElementById('detectionsList');
    const timestamp = new Date().toLocaleTimeString();
    
    // Remove empty state if it exists
    const emptyState = detectionsList.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const detectionItem = document.createElement('div');
    detectionItem.className = 'detection-item';
    detectionItem.style.opacity = '0';
    detectionItem.style.transform = 'translateX(-20px)';
    
    detectionItem.innerHTML = `
        <div class="detection-info">
            <span class="timestamp">${timestamp}</span>
            <span class="face-count">${faceCount} detection${faceCount !== 1 ? 's' : ''}</span>
        </div>
        ${frameUrl ? `<div class="detection-preview"><img src="${frameUrl}?t=${Date.now()}" alt="Detection" /></div>` : ''}
    `;

    detectionsList.insertBefore(detectionItem, detectionsList.firstChild);

    // Animate entrance
    setTimeout(() => {
        detectionItem.style.transition = 'all 0.4s ease-out';
        detectionItem.style.opacity = '1';
        detectionItem.style.transform = 'translateX(0)';
    }, 10);

    // Limit to 10 items
    while (detectionsList.children.length > 10) {
        const lastItem = detectionsList.lastChild;
        lastItem.style.transition = 'all 0.3s ease-in';
        lastItem.style.opacity = '0';
        lastItem.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            if (lastItem.parentNode) {
                lastItem.remove();
            }
        }, 300);
    }
}

function updateDetectionCount() {
    const countElement = document.getElementById('detectionCount');
    const currentCount = parseInt(countElement.textContent);
    const newCount = detectionCount;
    
    // Animate count change
    animateNumberChange('detectionCount', newCount, 'detection');
}

function animateNumberChange(elementId, newValue, suffix = '') {
    const element = document.getElementById(elementId);
    
    // Check if element exists
    if (!element) {
        console.warn(`Element with id '${elementId}' not found`);
        return;
    }
    
    const currentValue = parseInt(element.textContent) || 0;
    const increment = (newValue - currentValue) / 20;
    let current = currentValue;
    
    const animate = () => {
        current += increment;
        if ((increment > 0 && current >= newValue) || (increment < 0 && current <= newValue)) {
            element.textContent = newValue + (suffix ? ` ${suffix}` : '');
        } else {
            element.textContent = Math.floor(current) + (suffix ? ` ${suffix}` : '');
            requestAnimationFrame(animate);
        }
    };
    
    animate();
}

function startUptimeCounter() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
    
    const updateUptime = () => {
        if (startTime && isDetecting) {
            const now = new Date();
            const diff = Math.floor((now - startTime) / 1000);
            const minutes = Math.floor(diff / 60);
            const seconds = diff % 60;
            
            document.getElementById('uptime').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            animationFrameId = requestAnimationFrame(updateUptime);
        }
    };
    
    updateUptime();
}

function stopUptimeCounter() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
    document.getElementById('uptime').textContent = '00:00';
}

function showNotification(message, type = 'info') {
    try {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
            z-index: 1000;
            transform: translateX(400px);
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            max-width: 300px;
        `;
        
        // Add type-specific styling
        if (type === 'success') {
            notification.style.borderColor = '#4ECDC4';
            notification.style.background = 'linear-gradient(135deg, rgba(78, 205, 196, 0.1) 0%, rgba(78, 205, 196, 0.05) 100%)';
        } else if (type === 'warning') {
            notification.style.borderColor = '#FFE66D';
            notification.style.background = 'linear-gradient(135deg, rgba(255, 230, 109, 0.1) 0%, rgba(255, 230, 109, 0.05) 100%)';
        } else if (type === 'error') {
            notification.style.borderColor = '#FF6B6B';
            notification.style.background = 'linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 107, 107, 0.05) 100%)';
        }
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(400px)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 400);
            }
        }, 5000);
        
    } catch (error) {
        console.error('Error showing notification:', error);
        // Fallback to alert if notification fails
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

function logout() {
    // Add logout animation
    document.body.style.transition = 'all 0.5s ease-in';
    document.body.style.opacity = '0';
    document.body.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        window.location.href = '/logout';
    }, 500);
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('snapshotModal');
    if (e.target === modal) {
        closeSnapshotModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('snapshotModal');
        if (modal.classList.contains('active')) {
            closeSnapshotModal();
        }
    }
});

// Add CSS for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    
    .notification-message {
        color: var(--text-primary);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 6px;
        transition: all 0.3s ease;
        flex-shrink: 0;
    }
    
    .notification-close:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
    }
    
    .detection-info {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .detection-preview img {
        width: 80px;
        height: 60px;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid var(--card-border);
    }
`;

document.head.appendChild(notificationStyles);
