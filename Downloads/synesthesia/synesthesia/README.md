# Synesthesia

A real-time Python application that visualizes hand gestures and sounds as colorful shapes over your webcam feed.

## Features
- **Hand Gesture Detection (MediaPipe):**
  - Clap (hands come together quickly) → Purple Circle
  - Thumbs Up (only thumb extended) → Yellow Star
  - Wave/Hi (open palm, lateral movement) → Sky Blue Square
- **Sound Detection (sounddevice):**
  - Clap sound (short, high amplitude) → Purple Circle
  - Humming (sustained low pitch, 100–200 Hz) → Blue Triangle
  - Snap (short, sharp frequency burst) → Red Diamond
- **Shape Overlays:**
  - Shapes are drawn in real-time as overlays on the webcam feed using OpenCV.
- **Debounce Mechanism:**
  - Prevents rapid duplicate triggers for both gestures and sounds.
- **Modular Design:**
  - Easily extensible for new gestures, sounds, or shape mappings.

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure your webcam and microphone are connected and accessible.

## Running the App
```bash
python synesthesia.py
```

- Press `q` to quit the application.

## Extending
- Add new gestures in `synesthesia/gesture_detection.py`.
- Add new sound patterns in `synesthesia/sound_detection.py`.
- Add new shapes or mappings in `synesthesia/shape_rendering.py`.

## Requirements
- Python 3.7+
- OpenCV
- MediaPipe
- sounddevice
- numpy
- scipy

---

**Enjoy visualizing your gestures and sounds!** 