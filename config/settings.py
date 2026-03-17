# Paramètres de la caméra
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Écran (récupération à la demande)
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def get_screen_size():
    """Retourne la taille de l'écran (fallback à 640x480 si pyautogui échoue)."""
    global SCREEN_WIDTH, SCREEN_HEIGHT
    if SCREEN_WIDTH != 640 or SCREEN_HEIGHT != 480:
        return SCREEN_WIDTH, SCREEN_HEIGHT

    try:
        import pyautogui
        SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
        return SCREEN_WIDTH, SCREEN_HEIGHT
    except Exception:
        return SCREEN_WIDTH, SCREEN_HEIGHT

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

GESTURE_THRESHOLDS = {
    # ===== SEUILS DE BASE =====
    
    # Comptage des doigts (comparaison verticale)
    'finger_up_threshold': 0.02,    # Marge pour considérer un doigt levé
                                    # (le bout doit être plus haut que l'articulation)
    
    # ===== GESTE OK =====
    
    'ok_threshold': 0.05,           # Distance max entre pouce et index
                                    # 0.05 = 5% de la largeur de l'écran
    'ok_fingers_up': True,          # Les autres doigts doivent-ils être levés ?
    
    # ===== ÉCARTEMENT DES DOIGTS =====
    
    'finger_spread': 0.1,            # Écart minimum entre doigts pour "main ouverte"
    'peace_spread': 0.08,            # Écart spécifique pour le signe peace
    'zoom_spread': 0.15,             # Écart pour gestes de zoom
    
    # ===== GESTES DYNAMIQUES (SWIPE) =====
    
    'swipe_threshold': 0.2,          # Amplitude minimale du mouvement (20% écran)
    'swipe_history': 10,              # Nombre de frames à garder en mémoire
    'swipe_min_frames': 5,            # Frames minimum pour détecter un swipe
    
    # ===== GESTES DE LA MAIN =====
    
    'fist_fingers_down': 4,           # Nombre de doigts baissés pour un poing
    'open_hand_fingers_up': 5,        # Nombre de doigts levés pour main ouverte
    
    # ===== GESTES AVANCÉS (optionnel) =====
    
    'pinch_threshold': 0.03,          # Distance pour pincement (pouce-index)
    'rotation_threshold': 0.3,         # Angle pour détection rotation
    'two_hands_distance': 0.3,         # Distance entre deux mains
}