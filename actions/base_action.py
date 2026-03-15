from abc import ABC, abstractmethod

class BaseAction(ABC):
    """Classe abstraite pour tous les actions"""
    
    @abstractmethod
    def execute(self):
        """Exécute l'action"""
        pass
    