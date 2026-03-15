import cv2
import sys
from core.hand_detector import HandDetector
from core.gesture_recognizer import GestureRecognizer

cap = cv2.VideoCapture(0)
detector = HandDetector() 

try:
    while True:
        success, img = cap.read()
        gesture_recognizer = GestureRecognizer()
        img = detector.find_hands(img)
        landmarks = detector.find_position(img)
        
        if landmarks:
            print(gesture_recognizer.recognize(landmarks))
        cv2.imshow("Hand Detection", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except KeyboardInterrupt:
    sys.exit()

finally : 
    cap.release()
    cv2.destroyAllWindows()
