import math
import time
from gestures.base_gesture import BaseGesture
from config.settings import PINCH_THRESHOLD

class DoublePinch(BaseGesture):
    
    def __init__(self):
        self.last_pinch_time = 0
        self.pinching = False
        self.DOUBLE_CLICK_DELAY = 0.4
    
    @property
    def name(self):
        return "DOUBLE_PINCH"
    
    def detect(self, hand_landmarks):
        thumb = hand_landmarks[4]
        index = hand_landmarks[8]

        dist = math.sqrt((thumb[1] - index[1])**2 + (thumb[2] - index[2])**2)
        
        return (dist < PINCH_THRESHOLD and (time.time() - self.last_pinch_time < self.DOUBLE_CLICK_DELAY))
