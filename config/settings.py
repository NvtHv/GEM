import pyautogui

# Paramètres de la caméra
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

#Écran (récupéré automatiquement) modif 1
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

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
    'GESTURE_BG': (0, 0, 0),  # Noir
    'PINCH':           (0, 0, 255),   #  pour pinch.py
    'GESTURE_TEXT':    (0, 255, 255), #  pour l'overlay
}


#Souris (plus fuide dans les mouvements) modif 1
SMOOTHING_FACTOR = 7      
PINCH_THRESHOLD  = 5
SCROLL_SPEED     = 3      
DRAG_THRESHOLD   = 30 

#Zone active caméra (évite les bords) modif 1
CAM_MARGIN = 50

#sensibilité de la deplacement de la souris 
SENSITIVITY = 2