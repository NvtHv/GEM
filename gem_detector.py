import cv2, time
from core.hand_detector import HandDetector
from gestures import OpenHand, IndexPointUp, TwoFingersUp, PinkyUp, MiddleRingUp


def run_detection(stop_fn=None, gesture_callback=None, mirror=True):
    detector = HandDetector()
    gestures = [
        OpenHand(),
        IndexPointUp(),
        TwoFingersUp(),
        PinkyUp(),
        MiddleRingUp()
    ]

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera impossible à ouvrir")
        return

    last_gesture = None        # ← cooldown
    last_time = 0              # ← cooldown
    COOLDOWN = 1.0             # ← secondes, ajustable

    try:
        while True:
            if stop_fn and stop_fn():
                break

            success, img = cap.read()
            if not success:
                continue

            if mirror:
                img = cv2.flip(img, 1)

            img = detector.find_hands(img)
            landmarks = detector.find_position(img)

            gesture_emitted = False
            if landmarks:
                for g in gestures:
                    if g.detect(landmarks):
                        gesture_emitted = True
                        now = time.time()
                        if (g.name != last_gesture or        # ← cooldown
                                now - last_time > COOLDOWN): # ← cooldown
                            last_gesture = g.name            # ← cooldown
                            last_time = now                  # ← cooldown
                            if gesture_callback:
                                try:
                                    gesture_callback(g.name)
                                except Exception as e:
                                    print(f"Gesture callback error: {e}")
                            else:
                                g.action(landmarks)
                        break  # ← on s'arrête au premier geste détecté

            if not gesture_emitted and gesture_callback:
                gesture_callback(None)
                last_gesture = None    # ← reset si plus de geste détecté

            cv2.imshow('GEM Detection', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
