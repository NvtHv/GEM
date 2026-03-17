from config.settings import THUMB_TIP_ID, INDEX_TIP_ID, PINCH_THRESHOLD
from gestures.base_gesture import BaseGesture

class ZoomOut(BaseGesture):
    @property
    def name(self):
        return "ZOOM_OUT"

    def detect(self, landmarks):
        if len(landmarks) <= max(THUMB_TIP_ID, INDEX_TIP_ID):
            return False

        thumb = landmarks[THUMB_TIP_ID]
        index = landmarks[INDEX_TIP_ID]

        dx = thumb[1] - index[1]
        dy = thumb[2] - index[2]
        dist = (dx**2 + dy**2) ** 0.5

        return dist < PINCH_THRESHOLD

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Zoom out (PDF / Video)")

