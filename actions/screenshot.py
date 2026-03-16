import os
from datetime import datetime

class Screenshot:
    def execute(self):
        # sauvegarde un screenshot rapide dans le dossier courant
        try:
            from PIL import ImageGrab
            base = os.getcwd()
            filename = f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
            path = os.path.join(base, filename)
            ImageGrab.grab().save(path)
            print(f"Screenshot saved: {path}")
        except Exception as e:
            print(f"Screenshot action failed: {e}")
