import customtkinter as ctk
from tkinter import filedialog
import vlc
import os

class MP4Player(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.instance = None
        self.player = None
        self.current_file = None
        self.is_playing = False

        # Titre
        self.label = ctk.CTkLabel(self, text="📽️ Lecteur MP4", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=10)

        # Frame pour la vidéo
        self.video_frame = ctk.CTkFrame(self, width=640, height=360, fg_color="black")
        self.video_frame.pack(pady=10, padx=10)
        self.video_frame.pack_propagate(False)

        self.placeholder_label = ctk.CTkLabel(
            self.video_frame, 
            text="🎬 Aucune vidéo chargée", 
            font=ctk.CTkFont(size=20),
            text_color="gray"
        )
        self.placeholder_label.pack(expand=True, fill="both")

        self.open_btn = ctk.CTkButton(self, text="📂 Ouvrir un MP4", command=self.open_mp4)
        self.open_btn.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="Aucun fichier sélectionné.")
        self.status_label.pack(pady=5)

        # Contrôles
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=8)

        self.play_btn = ctk.CTkButton(self.control_frame, text="▶", width=60, command=self.play)
        self.play_btn.grid(row=0, column=0, padx=4)

        self.pause_btn = ctk.CTkButton(self.control_frame, text="⏸", width=60, command=self.pause)
        self.pause_btn.grid(row=0, column=1, padx=4)

        self.stop_btn = ctk.CTkButton(self.control_frame, text="⏹", width=60, command=self.stop)
        self.stop_btn.grid(row=0, column=2, padx=4)

        # Slider de progression
        self.progress_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.seek)
        self.progress_slider.pack(pady=5, fill="x", padx=20)
        self.progress_slider.set(0)

        # Label de temps
        self.time_label = ctk.CTkLabel(self, text="00:00 / 00:00")
        self.time_label.pack(pady=2)

        # Contrôle du volume
        self.volume_frame = ctk.CTkFrame(self)
        self.volume_frame.pack(pady=5, fill="x", padx=20)

        self.volume_label = ctk.CTkLabel(self.volume_frame, text="🔊", width=30)
        self.volume_label.pack(side="left", padx=5)

        self.volume_slider = ctk.CTkSlider(self.volume_frame, from_=0, to=100, command=self.set_volume)
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.volume_slider.set(80)

        # Initialisation
        self.after(500, self._setup_player)
        self.update_progress()

    def _setup_player(self):
        try:
            # On crée l'instance (enlever --no-audio pour avoir du son)
            self.instance = vlc.Instance("--quiet") 
            self.player = self.instance.media_player_new()
            
            # Intégration Windows
            if os.name == 'nt':
                self.player.set_hwnd(self.video_frame.winfo_id())
            # Note: Pour Linux, il faudrait utiliser set_xwindow
                
            print("✅ Player VLC initialisé")
        except Exception as e:
            print(f"❌ Erreur initialisation VLC: {e}")
            self.status_label.configure(text="Erreur: VLC n'est pas installé sur le système")

    def open_mp4(self):
        path = filedialog.askopenfilename(
            filetypes=[("Vidéo", "*.mp4 *.avi *.mkv *.mov"), ("Tous", "*.*")]
        )
        if path:
            self.current_file = path
            self.placeholder_label.pack_forget()
            media = self.instance.media_new(self.current_file)
            self.player.set_media(media)
            self.status_label.configure(text=f"Fichier : {os.path.basename(path)}")
            self.play()

    def play(self):
        if self.player and self.current_file:
            self.player.play()
            self.is_playing = True

    def pause(self):
        if self.player:
            self.player.pause()
            self.is_playing = False

    def stop(self):
        if self.player:
            self.player.stop()
            self.progress_slider.set(0)
            self.is_playing = False

    def seek(self, value):
        if self.player:
            self.player.set_position(float(value) / 100)

    def set_volume(self, value):
        if self.player:
            self.player.audio_set_volume(int(float(value)))

    def update_progress(self):
        if self.player and self.is_playing:
            length = self.player.get_length()
            time = self.player.get_time()
            if length > 0:
                pos = (time / length) * 100
                self.progress_slider.set(pos)
                self.time_label.configure(text=f"{self._format_time(time)} / {self._format_time(length)}")
        
        self.after(500, self.update_progress)

    def _format_time(self, ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"
    
    def increase_volume(self, step=10):
        """Augmente le volume"""
        if self.player:
            current = self.volume_slider.get()
            new = min(100, current + step)
            self.volume_slider.set(new)
            self.set_volume(new)

    def decrease_volume(self, step=10):
        """Diminue le volume"""
        if self.player:
            current = self.volume_slider.get()
            new = max(0, current - step)
            self.volume_slider.set(new)
            self.set_volume(new)

    def toggle_play_pause(self):
        if self.player and self.player.get_media():
            if self.player.is_playing():
                self.pause()
            else:
                self.play()
