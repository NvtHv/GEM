import customtkinter as ctk
from PIL import Image, ImageTk
import os

class SplashScreen(ctk.CTk):
    def __init__(self, delay=3000):
        super().__init__()
        self.delay = delay
        self.geometry("500x350")  # un peu plus haut pour tout le contenu
        self.overrideredirect(True)  # supprime la barre de titre

        # --- Chemins absolus vers les logos ---
        base_path = os.path.dirname(os.path.abspath(__file__))  # UI/
        gem_path = os.path.join(base_path, "assets", "logo_gem_n.jpeg")
        ispm_path = os.path.join(base_path, "assets", "logo_ispm.png")

        # --- Chargement des logos ---
        self.logo_gem = Image.open(gem_path)
        self.logo_gem = self.logo_gem.resize((100, 100), Image.Resampling.LANCZOS)
        self.logo_gem_tk = ImageTk.PhotoImage(self.logo_gem)

        self.logo_ispm = Image.open(ispm_path)
        self.logo_ispm = self.logo_ispm.resize((100, 100), Image.Resampling.LANCZOS)
        self.logo_ispm_tk = ImageTk.PhotoImage(self.logo_ispm)

        # --- Frame pour les logos côte à côte ---
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(pady=(30, 10))

        ctk.CTkLabel(logo_frame, image=self.logo_gem_tk, text="").pack(side="left", padx=20)
        ctk.CTkLabel(logo_frame, image=self.logo_ispm_tk, text="").pack(side="left", padx=20)

        # --- Texte principal ---
        ctk.CTkLabel(self, text="GEM Application", font=("Arial", 20, "bold")).pack(pady=(10, 5))

        # --- Sous-titre ---
        ctk.CTkLabel(self, text="Gesture Echo of Movement", font=("Arial", 14, "italic")).pack(pady=(0, 15))

        # --- Texte Chargement ---
        ctk.CTkLabel(self, text="Chargement...", font=("Arial", 14)).pack(pady=(0, 20))

        # Ferme le splash après le délai
        self.after(self.delay, self.close_splash)

    def close_splash(self):
        self.destroy()