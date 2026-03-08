from abc import ABC, abstractmethod

class BaseGesture(ABC):
    """Classe abstraite pour tous les gestes"""
    
    @abstractmethod
    def detect(self, hand_landmarks):
        """Détecte si le geste est présent"""
        pass
    
    @property
    @abstractmethod
    def name(self):
        """Nom du geste"""
        pass