import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
from ui.pdf_viewer import PDFViewer
from ui.mp3_player import MP3Player
from ui.mp4_player import MP4Player
from ui.photo_viewer import PhotoViewer
from gem_detector import run_detection

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("GEM - Gesture Echo of Movement")
        self.geometry("1024x700")
        self.minsize(860, 560)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Header ---
        self.header = ctk.CTkFrame(self, height=70, fg_color="#1f1f2a")
        self.header.pack(side="top", fill="x")

        self.logo = ctk.CTkLabel(self.header, text="GEM", font=ctk.CTkFont(size=28, weight="bold"))
        self.logo.pack(side="left", padx=20, pady=10)

        self.gem_state_indicator = ctk.CTkLabel(self.header, text="OFF", width=60, height=28, corner_radius=14, fg_color="#ff3b30", text_color="#ffffff")
        self.gem_state_indicator.pack(side="right", padx=12, pady=16)

        self.gem_switch = ctk.CTkSwitch(self.header, text="Activer GEM", command=self.toggle_gem)
        self.gem_switch.pack(side="right", padx=12, pady=14)

        # --- Navigation par Onglets ---
        # On ajoute le paramètre 'command' pour détecter le clic sur un onglet
        self.tab_view = ctk.CTkTabview(self, width=1024, height=600, fg_color="#262638", command=self._on_tab_changed)
        self.tab_view.pack(side="top", fill="both", expand=True, padx=20, pady=(15, 20))

        self.tabs = {
            "PDF": PDFViewer(self.tab_view.add("PDF")),
            "MP3": MP3Player(self.tab_view.add("MP3")),
            "MP4": MP4Player(self.tab_view.add("MP4")),
            "Photos": PhotoViewer(self.tab_view.add("Photos"))
        }

        for frame in self.tabs.values():
            frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Logique GEM ---
        self.gem_enabled = False
        self.gem_thread = None
        self.gem_stop_event = threading.Event()
        self.gesture_active = {'OPENED_HAND': False, 'INDEX_POINT_UP': False, 'TWO_FINGERS_UP': False}

    @property
    def current_view(self):
        return self.tabs.get(self.tab_view.get())

    def _on_tab_changed(self):
        """Arrête les médias des onglets inactifs lors d'un changement de vue."""
        current_name = self.tab_view.get()
        
        for name, view in self.tabs.items():
            if name != current_name:
                # Si la vue possède une méthode stop ou pause, on l'appelle
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
            self.gem_state_indicator.configure(text="ON", fg_color="#32d74b", text_color="#000000")
            self.start_gem_detection()
        else:
            self.gem_enabled = False
            self.gem_state_indicator.configure(text="OFF", fg_color="#ff3b30", text_color="#ffffff")
            self.stop_gem_detection()

    def start_gem_detection(self):
        if self.gem_thread and self.gem_thread.is_alive(): return
        self.gem_stop_event.clear()
        self.gem_thread = threading.Thread(target=self._gem_thread_loop, daemon=True)
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
        if not view: return

        if gesture_name is None:
            for key in self.gesture_active: self.gesture_active[key] = False
            return

        if gesture_name in self.gesture_active:
            if not self.gesture_active[gesture_name]:
                self.gesture_active[gesture_name] = True
                self._dispatch_action(gesture_name, view)
        else:
            self._dispatch_action(gesture_name, view)

    def _dispatch_action(self, gesture, view):
        tab_name = self.tab_view.get()
        if gesture == 'OPENED_HAND':
            if hasattr(view, 'toggle_play_pause'): view.toggle_play_pause()
        elif gesture == 'INDEX_POINT_UP':
            if hasattr(view, 'increase_volume'): view.increase_volume()
            elif tab_name == 'PDF' and hasattr(view, 'zoom_in'): view.zoom_in()
        elif gesture == 'TWO_FINGERS_UP':
            if hasattr(view, 'decrease_volume'): view.decrease_volume()
            elif tab_name == 'PDF' and hasattr(view, 'zoom_out'): view.zoom_out()
        # elif gesture == 'ZOOM_IN':
        #     if hasattr(view, 'zoom_in'): view.zoom_in()
        # elif gesture == 'ZOOM_OUT':
        #     if hasattr(view, 'zoom_out'): view.zoom_out()
        # elif gesture == 'SWIPE_RIGHT':
        #     if tab_name == 'PDF' and hasattr(view, 'next_page'): view.next_page()
        #     elif hasattr(view, 'play'): view.play()
        # elif gesture == 'SWIPE_LEFT':
        #     if tab_name == 'PDF' and hasattr(view, 'prev_page'): view.prev_page()
            # elif hasattr(view, 'stop'): view.stop()
