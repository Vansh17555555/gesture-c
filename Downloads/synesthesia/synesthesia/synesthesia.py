"""
Synesthesia: Real-time gesture-to-shape visualizer (audio removed)
"""
import cv2
from synesthesia.gesture_detection import GestureDetector
from synesthesia.shape_rendering import ShapeRenderer

def main():
    gesture_detector = GestureDetector()
    shape_renderer = ShapeRenderer()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to quit.")
    last_event = None
    last_event_time = 0
    event_display_duration = 1.0  # seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        # Gesture detection
        gesture = gesture_detector.detect(frame)

        # Combine events (now only gesture)
        event = gesture
        now = cv2.getTickCount() / cv2.getTickFrequency()
        if event:
            last_event = event
            last_event_time = now
        # Show shape for a short duration after event
        if last_event and now - last_event_time < event_display_duration:
            frame = shape_renderer.draw(frame, last_event)

        cv2.imshow('Synesthesia', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 