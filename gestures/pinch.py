import math
from gestures.base_gesture import BaseGesture
from config.settings import PINCH_THRESHOLD

class Pinch(BaseGesture):
    @property
    def name(self):
        return "PINCH"
    
    def detect(self, hand_landmarks):
        thumb_tip = hand_landmarks[4]
        index_tip = hand_landmarks[8]
        distance = math.sqrt((thumb_tip[1] - index_tip[1])**2 + (thumb_tip[2] - index_tip[2])**2)
        
        return distance < PINCH_THRESHOLD

