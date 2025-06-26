import mediapipe as mp
import numpy as np
import time
import cv2

class GestureDetector:
    def __init__(self, debounce_time=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.last_gesture_time = {}
        self.debounce_time = debounce_time
        
        # State machine for clap detection
        self.clap_state = "apart"  # apart, approaching, clapped
        self.prev_dist = None
        self.prev_time = None
        
        # Parameters (tunable)
        self.dist_threshold_apart = 120  # pixels
        self.dist_threshold_close = 70   # pixels
        self.speed_threshold_close = 300  # pixels/sec (closing speed)
        self.speed_threshold_apart = 200  # pixels/sec (opening speed)

    def _debounce(self, gesture):
        now = time.time()
        last_time = self.last_gesture_time.get(gesture, 0)
        if now - last_time > self.debounce_time:
            self.last_gesture_time[gesture] = now
            return True
        return False

    def _get_min_distance(self, hand_landmarks, frame_shape):
        h, w = frame_shape[:2]
        hands = []
        
        for landmarks in hand_landmarks:
            # Calculate palm center (average of wrist and middle base)
            wrist = np.array([landmarks.landmark[0].x * w, 
                              landmarks.landmark[0].y * h])
            mid_base = np.array([landmarks.landmark[9].x * w, 
                                 landmarks.landmark[9].y * h])
            palm = (wrist + mid_base) / 2
            hands.append(palm)
        
        if len(hands) == 2:
            return np.linalg.norm(hands[0] - hands[1])
        return None

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        gesture = None
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks
            print(f"Hands detected: {len(hand_landmarks)}")
            # --- Improved Clap: Two hands transition from far to close ---
            if len(hand_landmarks) == 2:
                h, w, _ = frame.shape
                hand1 = hand_landmarks[0].landmark[0]
                hand2 = hand_landmarks[1].landmark[0]
                x1, y1 = int(hand1.x * w), int(hand1.y * h)
                x2, y2 = int(hand2.x * w), int(hand2.y * h)
                dist = np.hypot(x2 - x1, y2 - y1)
                print(f"Wrist distance: {dist}")
                # Keep last 10 distances
                if not hasattr(self, 'clap_dist_history'):
                    self.clap_dist_history = []
                self.clap_dist_history.append(dist)
                if len(self.clap_dist_history) > 10:
                    self.clap_dist_history.pop(0)
                # Check if in the last 10 frames, hands were far apart (>200)
                was_far = any(d > 200 for d in self.clap_dist_history[:-2])
                # Now close (<120)
                if was_far and dist < 120:
                    if self._debounce('clap_gesture'):
                        print("Improved clap gesture detected!")
                        print("Detected gesture: clap_gesture")
                        return 'clap_gesture'
            else:
                self.clap_state = "apart"
                self.prev_dist = None

            # Process other gestures (thumbs up, wave)
            for handLms in hand_landmarks:
                tips = [4, 8, 12, 16, 20]
                fingers = []
                
                # Thumb (different landmark comparison)
                if handLms.landmark[4].x < handLms.landmark[3].x:
                    fingers.append(1)
                else:
                    fingers.append(0)
                
                # Other fingers
                for tip in tips[1:]:
                    if handLms.landmark[tip].y < handLms.landmark[tip-2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                # Thumbs up detection
                if fingers == [1, 0, 0, 0, 0]:
                    if self._debounce('thumbs_up'):
                        gesture = 'thumbs_up'
                
                # Wave detection
                if fingers == [1, 1, 1, 1, 1]:
                    if not hasattr(self, 'wave_prev_time'):
                        self.wave_prev_time = time.time()
                        self.wave_start_pos = handLms.landmark[0].x
                    else:
                        if time.time() - self.wave_prev_time < 1.0:  # Time window
                            current_pos = handLms.landmark[0].x
                            movement = abs(current_pos - self.wave_start_pos) * frame.shape[1]
                            if movement > 60:  # Minimum travel distance
                                if self._debounce('wave'):
                                    gesture = 'wave'
                        else:
                            # Reset wave tracking
                            self.wave_prev_time = time.time()
                            self.wave_start_pos = handLms.landmark[0].x

        return gesture