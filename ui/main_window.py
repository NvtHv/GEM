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
        self.gem_thread = None
        self.gem_stop_event = threading.Event()

        # Etats pour éviter les toggles répétés sur geste tenu
        self.gesture_active = {
            'CLOSED_FIST': False,
            'INDEX_POINT_UP': False,
        }

    def on_close(self):
        """Demande confirmation avant de fermer la fenêtre."""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter GEM ?"):
            self.destroy()

    def set_gem_active(self):
        """Active/désactive GEM et met à jour l'indicateur visuel."""
        if self.gem_switch.get() == 1:
            self.gem_enabled = True
            self.gem_state_indicator.configure(text="ON", fg_color="#32d74b", text_color="#000000")
            self.start_gem_detection()
        else:
            self.gem_enabled = False
            self.gem_state_indicator.configure(text="OFF", fg_color="#ff3b30", text_color="#ffffff")
            self.stop_gem_detection()

    def start_gem_detection(self):
        if self.gem_thread and self.gem_thread.is_alive():
            return

        self.gem_stop_event.clear()
        self.gem_thread = threading.Thread(target=self._gem_thread_loop, daemon=True)
        self.gem_thread.start()

    def stop_gem_detection(self):
        self.gem_stop_event.set()

    def _gem_thread_loop(self):
        run_detection(stop_fn=self.gem_stop_event.is_set, gesture_callback=self.handle_gesture)

    def handle_gesture(self, gesture_name):
        current = self.tab_view.get()

        if gesture_name is None:
            self.gesture_active['CLOSED_FIST'] = False
            self.gesture_active['INDEX_POINT_UP'] = False
            return

        if gesture_name == 'INDEX_MOVE':
            if current == 'PDF':
                self.pdf_frame.scroll_down()

        elif gesture_name == 'CLOSED_FIST':
            if not self.gesture_active['CLOSED_FIST']:
                self.gesture_active['CLOSED_FIST'] = True
                if current == 'MP3':
                    self.mp3_frame.toggle_play_pause()
                elif current == 'MP4':
                    self.mp4_frame.toggle_play_pause()

        elif gesture_name == 'INDEX_POINT_UP':
            if not self.gesture_active['INDEX_POINT_UP']:
                self.gesture_active['INDEX_POINT_UP'] = True
                self.mp3_frame.increase_volume()
                self.mp4_frame.increase_volume()

        elif gesture_name == 'ZOOM_IN':
            if current == 'PDF':
                self.pdf_frame.zoom_in()
            elif current == 'Photos':
                self.photo_frame.zoom_in()

        elif gesture_name == 'ZOOM_OUT':
            if current == 'PDF':
                self.pdf_frame.zoom_out()
            elif current == 'Photos':
                self.photo_frame.zoom_out()

        elif gesture_name == 'SWIPE_RIGHT':
            if current == 'PDF':
                self.pdf_frame.next_page()
            elif current == 'MP3':
                self.mp3_frame.play()
            elif current == 'MP4':
                self.mp4_frame.play()

        elif gesture_name == 'SWIPE_LEFT':
            if current == 'PDF':
                self.pdf_frame.prev_page()
            elif current == 'MP3':
                self.mp3_frame.stop()
            elif current == 'MP4':
                self.mp4_frame.stop()



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