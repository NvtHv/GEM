from gestures.base_gesture import BaseGesture
from config.settings import FINGER_TIP_IDS

class TwoFingersUp(BaseGesture):
    """
    Version simplifiée - deux doigts levés et serrés
    """

    @property
    def name(self):
        return "TWO_FINGERS_UP"
    
    def detect(self, hand_landmarks):
        two_fingers_up = True
        for i in range(1, 3):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]  # Articulation
            two_fingers_up = two_fingers_up and pip[2] > tip[2]
        for i in range(3, 5):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]  # Articulation
            two_fingers_up = two_fingers_up and tip[2] > pip[2]
        
        return two_fingers_up
        
    def action(self, landmarks):
        if self.detect(landmarks):
            print("Volume bas")
    