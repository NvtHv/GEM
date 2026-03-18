import customtkinter as ctk
from PIL import Image
import threading
import os

from ui.pdf_viewer import PDFViewer
from ui.mp3_player import MP3Player
from ui.mp4_player import MP4Player
from ui.photo_viewer import PhotoViewer
from gem_detector import run_detection


# =========================
# TOOLTIP CLASS
# =========================
class ToolTip:
    def __init__(self, widget, text, x_offset=-20):
        """
        x_offset : décalage horizontal (négatif = vers la gauche, positif = vers la droite)
        """
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.x_offset = x_offset

        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return

        # Position juste en dessous du widget + décalage horizontal
        x = self.widget.winfo_rootx() + self.x_offset
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            tw,
            text=self.text,
            fg_color="#333333",
            text_color="white",
            corner_radius=6,
            padx=10,
            pady=5
        )
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GEM - Gesture Echo of Movement")
        self.geometry("1024x700")
        self.minsize(860, 560)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- PATH ---
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Icône fenêtre
        icon_path = os.path.join(base_path, "assets", "icon_gem_n.ico")
        self.iconbitmap(icon_path)

        # --- Header ---
        self.header = ctk.CTkFrame(self, height=70, fg_color="#1f1f2a")
        self.header.pack(side="top", fill="x")

        # =========================
        # LOGO GEM (gauche)
        # =========================
        gem_path = os.path.join(base_path, "assets", "logo_gem_n.jpeg")
        gem_image = ctk.CTkImage(
            light_image=Image.open(gem_path),
            size=(50, 50)
        )
        self.logo_image = gem_image

        self.logo_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.logo_frame.pack(side="left", padx=20, pady=10)

        self.logo_img_label = ctk.CTkLabel(
            self.logo_frame,
            image=self.logo_image,
            text=""
        )
        self.logo_img_label.pack(side="left", padx=(0, 10))

        self.logo_text = ctk.CTkLabel(
            self.logo_frame,
            text="GEM",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#ffffff"
        )
        self.logo_text.pack(side="left")

        # =========================
        # LOGO ISPM (droite)
        # =========================
        ispm_path = os.path.join(base_path, "assets", "logo_ispm.png")
        ispm_img = ctk.CTkImage(
            light_image=Image.open(ispm_path),
            size=(50, 50)
        )
        self.ispm_image = ispm_img

        self.ispm_container = ctk.CTkFrame(self.header, fg_color="transparent")
        self.ispm_container.pack(side="right", padx=(5, 10))

        self.ispm_label = ctk.CTkLabel(
            self.ispm_container,
            image=self.ispm_image,
            text="",
            cursor="hand2"
        )
        self.ispm_label.pack(pady=10)

        # Tooltip ISPM
        ToolTip(self.ispm_label, "ISPM", x_offset=-10)

        # =========================
        # SWITCH + INDICATOR GEM
        # =========================
        self.gem_state_indicator = ctk.CTkLabel(
            self.header,
            text="OFF",
            width=60,
            height=28,
            corner_radius=14,
            fg_color="#ff3b30",
            text_color="#ffffff"
        )
        self.gem_state_indicator.pack(side="right", padx=12, pady=16)

        self.gem_switch = ctk.CTkSwitch(
            self.header,
            text="Activer GEM",
            command=self.toggle_gem
        )
        self.gem_switch.pack(side="right", padx=12, pady=14)

        # =========================
        # BOUTON AIDE / TUTORIEL
        # =========================
        self.help_button = ctk.CTkButton(
            self.header,
            text="?",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="#555555",
            hover_color="#777777",
            command=self.show_tutorial
        )
        self.help_button.pack(side="right", padx=(0, 10), pady=20)
        ToolTip(self.help_button, "Cliquez pour voir le tutoriel", x_offset=-10)

        # --- Onglets ---
        self.tab_view = ctk.CTkTabview(
            self,
            width=1024,
            height=600,
            fg_color="#262638",
            command=self._on_tab_changed
        )
        self.tab_view.pack(side="top", fill="both", expand=True, padx=20, pady=(15, 20))

        self.tabs = {
            "PDF": PDFViewer(self.tab_view.add("PDF")),
            "MP3": MP3Player(self.tab_view.add("MP3")),
            "MP4": MP4Player(self.tab_view.add("MP4")),
            "Photos": PhotoViewer(self.tab_view.add("Photos"))
        }

        for frame in self.tabs.values():
            frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- GEM Logic ---
        self.gem_enabled = False
        self.gem_thread = None
        self.gem_stop_event = threading.Event()

        self.gesture_active = {
            'OPENED_HAND': False,
            'INDEX_POINT_UP': False,
            'TWO_FINGERS_UP': False,
            'PINKY_UP': False,
            'MIDDLE_RING_UP': False
        }

    # =========================
    # PROPRIETES ET METHODES
    # =========================
    @property
    def current_view(self):
        return self.tabs.get(self.tab_view.get())

    def _on_tab_changed(self):
        current_name = self.tab_view.get()
        for name, view in self.tabs.items():
            if name != current_name:
                if hasattr(view, 'stop'):
                    view.stop()
                elif hasattr(view, 'pause'):
                    view.pause()

    def on_close(self):
        self.stop_gem_detection()
        self.destroy()

    def toggle_gem(self):
        if self.gem_switch.get() == 1:
            self.gem_enabled = True
            self.gem_state_indicator.configure(
                text="ON",
                fg_color="#32d74b",
                text_color="#000000"
            )
            self.start_gem_detection()
        else:
            self.gem_enabled = False
            self.gem_state_indicator.configure(
                text="OFF",
                fg_color="#ff3b30",
                text_color="#ffffff"
            )
            self.stop_gem_detection()

    def start_gem_detection(self):
        if self.gem_thread and self.gem_thread.is_alive():
            return
        self.gem_stop_event.clear()
        self.gem_thread = threading.Thread(
            target=self._gem_thread_loop,
            daemon=True
        )
        self.gem_thread.start()

    def stop_gem_detection(self):
        self.gem_stop_event.set()

    def _gem_thread_loop(self):
        run_detection(
            stop_fn=self.gem_stop_event.is_set,
            gesture_callback=lambda g: self.after(0, self.handle_gesture, g)
        )

    def handle_gesture(self, gesture_name):
        view = self.current_view
        if not view:
            return

        if gesture_name is None:
            for key in self.gesture_active:
                self.gesture_active[key] = False
            return

        if gesture_name in self.gesture_active:
            if not self.gesture_active[gesture_name]:
                self.gesture_active[gesture_name] = True
                self._dispatch_action(gesture_name, view)
        else:
            self._dispatch_action(gesture_name, view)

    def _dispatch_action(self, gesture, view):
        tab_name = self.tab_view.get()
        if gesture == 'OPENED_HAND' and hasattr(view, 'toggle_play_pause'):
            view.toggle_play_pause()
        elif gesture == 'INDEX_POINT_UP':
            if hasattr(view, 'increase_volume'):
                view.increase_volume()
            elif hasattr(view, 'zoom_in'):
                view.zoom_in()
        elif gesture == 'TWO_FINGERS_UP':
            if hasattr(view, 'decrease_volume'):
                view.decrease_volume()
            elif hasattr(view, 'zoom_out'):
                view.zoom_out()
        elif gesture == 'PINKY_UP':
            if hasattr(view, 'play_next'):
                view.play_next()
            elif hasattr(view, '_skip'):
                view._skip(5000)
            elif tab_name == 'PDF' and hasattr(view, 'next_page'):
                view.next_page()
        elif gesture == 'MIDDLE_RING_UP':
            if hasattr(view, 'play_previous'):
                view.play_previous()
            elif hasattr(view, '_skip'):
                view._skip(-5000)
            elif tab_name == 'PDF' and hasattr(view, 'prev_page'):
                view.prev_page()

    # =========================
    # FONCTION TUTORIEL
    # =========================
    def show_tutorial(self):
        tutorial_win = ctk.CTkToplevel(self)
        tutorial_win.title("Tutoriel GEM")
        tutorial_win.geometry("500x400")
        tutorial_win.grab_set()  # modal

        # --- Icône pour CTkToplevel ---
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon_gem_n.ico")
        try:
            tutorial_win.wm_iconbitmap(icon_path)  # wm_iconbitmap fonctionne mieux pour Toplevel
        except Exception as e:
            print(f"Impossible de changer l'icône du tuto : {e}")

        tutorial_text = """
    Bienvenue dans GEM - Gesture Echo of Movement !

    Instructions :
    1. Activer GEM avec le switch "Activer GEM".
    2. Utilisez vos gestes pour contrôler les médias :
    - Main ouverte : play/pause
    - Index levé : augmenter le volume / zoom in
    - Deux doigts levés : diminuer le volume / zoom out
    - Petit doigt levé : passer au suivant / page suivante
    - Majeur + annulaires levés : revenir au précédent / page précédente

    """
        label = ctk.CTkLabel(
            tutorial_win,
            text=tutorial_text,
            justify="left",
            padx=20,
            pady=20,
            text_color="#ffffff",
            fg_color="#262638",
            corner_radius=8
        )
        label.pack(fill="both", expand=True, padx=10, pady=10)