import customtkinter as ctk
import tkinter.messagebox as messagebox
from ui.pdf_viewer import PDFViewer
from ui.mp3_player import MP3Player
from ui.mp4_player import MP4Player
from ui.photo_viewer import PhotoViewer


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GEM")
        self.geometry("1024x700")
        self.minsize(860, 560)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Header
        self.header = ctk.CTkFrame(self, height=70, fg_color="#1f1f2a")
        self.header.pack(side="top", fill="x")

        self.logo = ctk.CTkLabel(self.header, text="GEM", font=ctk.CTkFont(size=28, weight="bold"))
        self.logo.pack(side="left", padx=20, pady=10)

        self.subtitle = ctk.CTkLabel(self.header, text="Gesture Echo of Movement", font=ctk.CTkFont(size=14), text_color="#d1d1df")
        self.subtitle.pack(side="left", pady=10)

        # GEM On/Off switch et témoin
        self.gem_state_indicator = ctk.CTkLabel(self.header, text="OFF", width=60, height=28, corner_radius=14, fg_color="#ff3b30", text_color="#ffffff")
        self.gem_state_indicator.pack(side="right", padx=12, pady=16)

        self.gem_switch = ctk.CTkSwitch(self.header, text="Activer GEM", command=self.set_gem_active)
        self.gem_switch.pack(side="right", padx=12, pady=14)

        # Tab view moderne
        self.tab_view = ctk.CTkTabview(self, width=1024, height=600, fg_color="#262638")
        self.tab_view.pack(side="top", fill="both", expand=True, padx=20, pady=(15, 20))

        self.tab_view.add("PDF")
        self.tab_view.add("MP3")
        self.tab_view.add("MP4")
        self.tab_view.add("Photos")

        self.tab_view.set("PDF")

        self.pdf_frame = PDFViewer(self.tab_view.tab("PDF"))
        self.pdf_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.mp3_frame = MP3Player(self.tab_view.tab("MP3"))
        self.mp3_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.mp4_frame = MP4Player(self.tab_view.tab("MP4"))
        self.mp4_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.photo_frame = PhotoViewer(self.tab_view.tab("Photos"))
        self.photo_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.gem_enabled = False

    def on_close(self):
        """Demande confirmation avant de fermer la fenêtre."""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter GEM ?"):
            self.destroy()

    def set_gem_active(self):
        """Active/désactive GEM et met à jour l'indicateur visuel."""
        if self.gem_switch.get() == 1:
            self.gem_enabled = True
            self.gem_state_indicator.configure(text="ON", fg_color="#32d74b", text_color="#000000")
        else:
            self.gem_enabled = False
            self.gem_state_indicator.configure(text="OFF", fg_color="#ff3b30", text_color="#ffffff")

    def _switch_view(self, view_class):
        """Change le panneau actif en détruisant l'ancien et en affichant le nouveau."""
        if self.current_view is not None:
            self.current_view.destroy()

        self.current_view = view_class(self.content)
        self.current_view.pack(fill="both", expand=True)
        """Change le panneau actif en détruisant l'ancien et en affichant le nouveau."""
        if self.current_view is not None:
            self.current_view.destroy()

        self.current_view = view_class(self.content)
        self.current_view.pack(fill="both", expand=True)