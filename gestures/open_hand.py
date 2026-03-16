from gestures.base_gesture import BaseGesture
from config.settings import FINGER_TIP_IDS

class OpenHand(BaseGesture):
    @property
    def name(self):
        return "OPEN_HAND"
    
    def detect(self, landmarks):
        fingers_up = 0
        for tip_id in FINGER_TIP_IDS:
            tip = landmarks[tip_id][2]
            pip = landmarks[tip_id - 2][2]
            if tip < pip:
                fingers_up += 1

        return fingers_up >= 4
    
    def action(self, landmarks):
        if self.detect(landmarks):
            print("Return to main menu")

