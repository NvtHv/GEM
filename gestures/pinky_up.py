from config.settings import FINGER_TIP_IDS
from gestures.base_gesture import BaseGesture


class PinkyUp(BaseGesture):
    """
    Auriculaire levé, les 3 autres doigts (index, majeur, annulaire) baissés.
    Action : piste suivante (next track)
    """

    @property
    def name(self):
        return "PINKY_UP"

    def detect(self, hand_landmarks):
        # Auriculaire (i=4) doit être levé
        tip = hand_landmarks[FINGER_TIP_IDS[4]]
        pip = hand_landmarks[FINGER_TIP_IDS[4] - 2]
        pinky_up = pip[2] > tip[2]

        # Index, majeur, annulaire (i=1,2,3) doivent être baissés
        for i in range(1, 4):
            tip = hand_landmarks[FINGER_TIP_IDS[i]]
            pip = hand_landmarks[FINGER_TIP_IDS[i] - 2]
            pinky_up = pinky_up and tip[2] > pip[2]

        return pinky_up

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Next track")
