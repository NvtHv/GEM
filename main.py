import cv2
from core.hand_detector import HandDetector

cap = cv2.VideoCapture(0)
detector = HandDetector()

while True:
    success, img = cap.read()

    img = detector.find_hands(img)
    landmarks = detector.find_position(img)

    if landmarks:
        print(landmarks[8])  # position du bout de l'index

    cv2.imshow("Hand Detection", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()