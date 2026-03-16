import cv2
import sys
from core.hand_detector import HandDetector
from gestures.pinch import Pinch
from gestures.doublepinch import DoublePinch
from gestures.open import Open
from gestures.fist import Fist
from gestures.peace import Peace

cap = cv2.VideoCapture(0)
detector = HandDetector()
pinch = Pinch()
doublepinch = DoublePinch()
open = Open()
fist = Fist()
peace = Peace()

try:
    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        landmarks = detector.find_position(img)
        
        if landmarks:
            pinch.action(landmarks)
            doublepinch.action(landmarks)
            open.action(landmarks)
            fist.action(landmarks)
            peace.action(landmarks)

        cv2.imshow("Hand Detection", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except KeyboardInterrupt:
    sys.exit()

finally : 
    cap.release()
    cv2.destroyAllWindows()
