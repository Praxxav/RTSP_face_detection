# RTSP Face Detection Hub 🚀

A modern, real-time face detection system with a **HOT** new UI featuring gradient colors, smooth animations, and sleek design.

## ✨ New Features

### 🎨 **Hot Modern UI**
- **Black Theme**: Sleek dark interface with glass-morphism effects
- **Gradient Colors**: Beautiful gradient combinations (red-to-cyan, blue-to-purple, pink-to-red)
- **Animated Background**: Floating gradient orbs with particle effects
- **Glass Cards**: Transparent cards with backdrop blur effects

### 🎭 **Smooth Animations**
- **Framer Motion**: Professional-grade animations and transitions
- **AOS Animations**: Scroll-triggered entrance animations
- **Hover Effects**: Interactive hover states with smooth transitions
- **Number Animations**: Smooth counting animations for statistics

### 🎯 **Enhanced UX**
- **Modern Typography**: Inter font family for better readability
- **Responsive Design**: Mobile-first responsive layout
- **Interactive Elements**: Hover effects, smooth transitions, and micro-interactions
- **Status Indicators**: Real-time status with animated dots
- **Notifications**: Toast notifications for user feedback

### 🔧 **Technical Improvements**
- **Modern CSS**: CSS custom properties, flexbox, and grid layouts
- **Performance**: Optimized animations with requestAnimationFrame
- **Accessibility**: Better contrast, focus states, and keyboard navigation
- **Cross-browser**: Modern CSS features with fallbacks

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Flask
- OpenCV
- YOLOv8

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd rtsp_face_detection

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

## 🎨 UI Components

### Color Scheme
- **Primary**: Red to Cyan gradient (#FF6B6B → #4ECDC4)
- **Secondary**: Blue to Purple gradient (#667eea → #764ba2)
- **Accent**: Pink to Red gradient (#f093fb → #f5576c)
- **Background**: Pure black (#000000)
- **Cards**: Semi-transparent white with blur effects

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800
- **Hierarchy**: Clear visual hierarchy with consistent spacing

### Animations
- **Entrance**: Fade-in and slide-up animations
- **Hover**: Lift effects and scale transformations
- **Transitions**: Smooth 0.3s ease transitions
- **Loading**: Pulse animations for status indicators

## 📱 Responsive Design

- **Desktop**: Full-featured layout with side-by-side sections
- **Tablet**: Stacked layout with optimized spacing
- **Mobile**: Single-column layout with touch-friendly controls

## 🎯 Key Features

1. **Real-time Detection**: Live video stream with face detection
2. **Statistics Dashboard**: Real-time metrics and performance indicators
3. **Configuration Panel**: Easy-to-use settings management
4. **Detection History**: Scrollable list of recent detections
5. **Snapshot Capture**: Capture and view detection images
6. **Status Monitoring**: Real-time connection and detection status

## 🔧 Configuration

The system supports various configuration options:
- RTSP stream URL
- Frame dimensions
- Detection parameters
- Performance settings

## 🚀 Performance Features

- **Optimized Rendering**: Efficient canvas-based snapshot capture
- **Smooth Animations**: 60fps animations with requestAnimationFrame
- **Lazy Loading**: Progressive enhancement for better performance
- **Memory Management**: Efficient cleanup of old detection items

## 🎨 Customization

### Colors
Modify CSS custom properties in `static/styles.css`:
```css
:root {
    --primary-gradient: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
    --secondary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* ... more variables */
}
```

### Animations
Adjust animation timing and easing:
```css
.stat-card {
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-4px);
}
```

## 🌟 Future Enhancements

- [ ] Dark/Light theme toggle
- [ ] Custom color schemes
- [ ] Advanced animation presets
- [ ] Performance monitoring dashboard
- [ ] Export/import configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Framer Motion** for smooth animations
- **AOS** for scroll animations
- **Inter Font** for beautiful typography
- **OpenCV** for computer vision capabilities

---

**Made with ❤️ and lots of gradients!** 🎨✨