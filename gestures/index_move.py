from config.settings import FINGER_TIP_IDS
from gestures.base_gesture import BaseGesture

class IndexMove(BaseGesture):
    def __init__(self):
        self.prev_x = None
        self.prev_y = None

    @property
    def name(self):
        return "INDEX_MOVE"

    def detect(self, landmarks):
        if len(landmarks) <= 8:
            return False

        # index finger tip = id8
        x = landmarks[8][1]
        y = landmarks[8][2]

        # doigt levé : index_tip plus haut que pip
        if landmarks[8][2] >= landmarks[6][2]:
            return False

        if self.prev_x is None or self.prev_y is None:
            self.prev_x, self.prev_y = x, y
            return False

        dx, dy = x - self.prev_x, y - self.prev_y
        self.prev_x, self.prev_y = x, y

        return abs(dx) > 10 or abs(dy) > 10

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Move cursor / scroll PDF")
