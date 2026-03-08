# Paramètres de la caméra
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Paramètres MediaPipe
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 2

# Seuils pour la détection des gestes
FINGER_TIP_IDS = [4, 8, 12, 16, 20]  # Bouts des doigts
THUMB_TIP_ID = 4
INDEX_TIP_ID = 8

# Couleurs (BGR)
COLORS = {
    'HAND_LANDMARKS': (0, 255, 0),  # Vert
    'HAND_CONNECTIONS': (255, 255, 255),  # Blanc
    'TEXT': (255, 0, 0),  # Bleu
    'GESTURE_BG': (0, 0, 0)  # Noir
}