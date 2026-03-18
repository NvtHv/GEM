import customtkinter as ctk
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen  # On crée ce fichier à côté

def main():
    # --- Configuration CustomTkinter ---
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # --- Splash Screen ---
    splash = SplashScreen(delay=2000)  # 2 secondes
    splash.update()  # Affiche le splash immédiatement
    splash.mainloop()  # Attend la fin du splash

    # --- Fenêtre principale ---
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()