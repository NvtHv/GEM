from gestures.base_gesture import BaseGesture

class SwipeRight(BaseGesture):
    def __init__(self):
        self.prev_x = None

    @property
    def name(self):
        return "SWIPE_RIGHT"

    def detect(self, landmarks):
        if len(landmarks) == 0:
            return False

        x = landmarks[0][1]
        if self.prev_x is None:
            self.prev_x = x
            return False

        dx = x - self.prev_x
        self.prev_x = x
        return dx > 40

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Next page / next song")
