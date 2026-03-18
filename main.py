import sys
from pathlib import Path
import customtkinter as ctk

# --- Gestion du Path (indispensable pour vos imports locaux) ---
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Imports de vos modules ---
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen
from gem_detector import run_detection

def start_ui():
    """Lance l'interface graphique avec Splash Screen"""
    # Configuration du thème
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Étape 1 : Splash Screen
    splash = SplashScreen(delay=2000)
    # Note : Suivant comment SplashScreen est codé, 
    # le mainloop() se fermera après le 'delay'.
    splash.mainloop() 

    # Étape 2 : Fenêtre principale
    app = MainWindow()
    app.mainloop()

if __name__ == '__main__':
    # Si run_detection() lance une boucle infinie ou bloquante,
    # assurez-vous qu'elle est appelée au bon moment.
    # Si vous voulez l'interface d'abord, appelez start_ui() :
    
    start_ui()