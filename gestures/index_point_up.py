from gestures.base_gesture import BaseGesture
from config.settings import FINGER_TIP_IDS

class IndexPointUp(BaseGesture):
    @property
    def name(self):
        return "INDEX_POINT_UP"

    def detect(self, landmarks):
        if len(landmarks) <= 8:
            return False

        # index finger vertical upwards et autres fermés
        index_up = landmarks[8][2] < landmarks[6][2]
        other_fingers = all(landmarks[i][2] > landmarks[i-2][2] for i in (12, 16, 20))

        return index_up and other_fingers

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Volume +")
