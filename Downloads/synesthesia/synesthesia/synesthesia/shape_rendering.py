import cv2
import numpy as np

class ShapeRenderer:
    def __init__(self):
        # Map event to (shape, color)
        self.event_map = {
            'clap_gesture': ('circle', (128, 0, 128)),      # Purple
            'thumbs_up': ('star', (0, 255, 255)),           # Yellow
            'wave': ('square', (135, 206, 235)),            # Sky Blue
            'clap_sound': ('circle', (128, 0, 128)),        # Purple
            'humming': ('triangle', (255, 0, 0)),           # Blue
            'snap': ('diamond', (0, 0, 255)),               # Red
        }

    def draw(self, frame, event):
        h, w, _ = frame.shape
        center = (w // 2, h // 2)
        shape, color = self.event_map.get(event, (None, (255, 255, 255)))
        overlay = frame.copy()
        if shape == 'circle':
            cv2.circle(overlay, center, 80, color, -1)
        elif shape == 'star':
            self._draw_star(overlay, center, 80, color)
        elif shape == 'square':
            cv2.rectangle(overlay, (center[0]-80, center[1]-80), (center[0]+80, center[1]+80), color, -1)
        elif shape == 'triangle':
            pts = np.array([
                [center[0], center[1]-90],
                [center[0]-80, center[1]+70],
                [center[0]+80, center[1]+70]
            ], np.int32)
            cv2.fillPoly(overlay, [pts], color)
        elif shape == 'diamond':
            pts = np.array([
                [center[0], center[1]-90],
                [center[0]-80, center[1]],
                [center[0], center[1]+90],
                [center[0]+80, center[1]]
            ], np.int32)
            cv2.fillPoly(overlay, [pts], color)
        # Blend overlay for transparency
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        return frame

    def _draw_star(self, img, center, size, color):
        # Draw a 5-pointed star
        pts = []
        for i in range(10):
            angle = i * np.pi / 5 - np.pi / 2
            r = size if i % 2 == 0 else size // 2
            x = int(center[0] + r * np.cos(angle))
            y = int(center[1] + r * np.sin(angle))
            pts.append((x, y))
        pts = np.array(pts, np.int32)
        cv2.fillPoly(img, [pts], color) 