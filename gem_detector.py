import cv2, time
from core.hand_detector import HandDetector
from gestures import IndexMove, Fist, ZoomIn, ZoomOut, SwipeLeft, SwipeRight, OpenHand, IndexPointUp


def run_detection(stop_fn=None, gesture_callback=None):
    detector = HandDetector()
    gestures = [
        IndexMove(),
        IndexPointUp(),
        OpenHand(),
        Fist(),
        ZoomIn(),
        ZoomOut(),
        SwipeLeft(),
        SwipeRight(),
    ]

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera impossible à ouvrir")
        return

    try:
        while True:
            if stop_fn and stop_fn():
                break

            success, img = cap.read()
            if not success:
                continue

            img = detector.find_hands(img)
            landmarks = detector.find_position(img)

            gesture_emitted = False
            if landmarks:
                for g in gestures:
                    if g.detect(landmarks):
                        gesture_emitted = True
                        if gesture_callback:
                            try:
                                gesture_callback(g.name)
                            except Exception as e:
                                print(f"Gesture callback error: {e}")
                        else:
                            g.action(landmarks)

            if not gesture_emitted and gesture_callback:
                gesture_callback(None)

            cv2.imshow('GEM Detection', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
