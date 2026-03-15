from config.settings import FINGER_TIP_IDS
from gestures.base_gesture import BaseGesture

class Peace(BaseGesture):
    @property
    def name(self):
        return "PAIX"
    
    def detect(self, hand_landmarks):
        """Détecte si la main est en signe de paix"""
        is_peace = True
        for i in range(1, 3):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]  # Articulation
            is_peace = is_peace and pip[2] > tip[2]
        for i in range(3, 5):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]  # Articulation
            is_peace = is_peace and tip[2] > pip[2]
        
        return is_peace
        
        