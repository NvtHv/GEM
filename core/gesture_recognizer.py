from gestures import get_all_gestures

class GestureRecognizer:
    
    def __init__(self):
        self.gestures = get_all_gestures()
    
    def recognize(self, landmarks):
        """Reconnaît le geste pour une main donnée"""
        for gesture in self.gestures:
            if gesture.detect(landmarks):
                return gesture.name
        return "Inconnu"