from actions.freeze import Freeze
from config.settings import FINGER_TIP_IDS
from gestures.base_gesture import BaseGesture
class Fist(BaseGesture):
    @property
    def name(self):
        return "POING"
    
    def detect(self, hand_landmarks):
        """Détecte si la main est fermée (poing)"""
        fingers_folded = 0

        for i in range(1, 5):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]
            if tip[2] > pip[2]:
                fingers_folded += 1
                
        return fingers_folded >= 4
    
    def action(self, landmarks):
        if self.detect(landmarks):
            Freeze().execute()