from gestures.base_gesture import BaseGesture

class SwipeLeft(BaseGesture):
    def __init__(self):
        self.prev_x = None

    @property
    def name(self):
        return "SWIPE_LEFT"

    def detect(self, landmarks):
        if len(landmarks) == 0:
            return False

        x = landmarks[0][1]
        if self.prev_x is None:
            self.prev_x = x
            return False

        dx = self.prev_x - x
        self.prev_x = x
        return dx > 40

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Previous page / previous song")
