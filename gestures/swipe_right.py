import time
from gestures.base_gesture import BaseGesture
from config.settings import GESTURE_THRESHOLDS

class SwipeRight(BaseGesture):
    """
    Détecte le geste swipe droit
    Évite les faux positifs lors du retour de la main
    """
    
    def __init__(self):
        self.history = []
        self.max_history = GESTURE_THRESHOLDS.get('swipe_history', 10)
        self.threshold = GESTURE_THRESHOLDS.get('swipe_threshold', 0.2)
        self.min_frames = GESTURE_THRESHOLDS.get('swipe_min_frames', 5)
        
        # État pour éviter les swipes de retour
        self.last_swipe_time = 0
        self.last_swipe_direction = None
        self.cooldown = 0.5  # 500ms de cooldown entre swipes

    @property
    def name(self):
        return "SWIPE_RIGHT"
        
    def detect(self, hand_landmarks):
        """
        Détecte un swipe droit
        Retourne True seulement si c'est un vrai swipe, pas un retour
        """
        # Position du poignet pour le mouvement
        wrist = hand_landmarks[0]
        current_pos = (wrist[1], wrist[2])
        
        # Ajoute à l'historique
        self.history.append(current_pos)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Pas assez de données
        if len(self.history) < self.min_frames:
            return False
        
        # Vérifie le cooldown
        current_time = time.time()
        if current_time - self.last_swipe_time < self.cooldown:
            return False
        
        # Calcule le mouvement global
        first_pos = self.history[0]
        last_pos = self.history[-1]
        
        dx = last_pos[0] - first_pos[0]
        dy = last_pos[1] - first_pos[1]
        
        # Détection swipe droit
        is_swipe_right = dx > self.threshold and abs(dy) < self.threshold / 2
        
        if is_swipe_right:
            # Vérifie que ce n'est pas un retour de swipe gauche
            if self.last_swipe_direction == "LEFT" and current_time - self.last_swipe_time < 1.0:
                # C'est probablement un retour, on ignore
                return False
            
            # C'est un vrai swipe droit
            self.last_swipe_time = current_time
            self.last_swipe_direction = "RIGHT"
            return True
        
        return False

    def action(self, landmarks):
        if self.detect(landmarks):
            print("Swipe right")