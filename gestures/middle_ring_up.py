from config.settings import FINGER_TIP_IDS
from gestures.base_gesture import BaseGesture

class MiddleRingUp(BaseGesture):
    """
    Majeur + annulaire levés, index + auriculaire baissés.
    Action : piste précédente (previous track)
    """

    @property
    def name(self):
        return "MIDDLE_RING_UP"

    def detect(self, hand_landmarks):
        # Majeur (2) et annulaire (3) doivent être levés
        for i in (2, 3):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]
            if not (pip[2] > tip[2]):
                return False

        # Index (1) et auriculaire (4) doivent être baissés
        for i in (1, 4):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]
            if not (tip[2] > pip[2]):
                return False

        return True

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Previous track")
