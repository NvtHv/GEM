import customtkinter as ctk
from tkinter import filedialog
import vlc
import os


class MP3Player(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.player = None
        self.current_file = None

        # Titre
        self.label = ctk.CTkLabel(self, text="MP3 Player", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=10)

        # Frame pour le lecteur vidéo intégré (pour l'aspect visuel)
        self.video_frame = ctk.CTkFrame(self, width=400, height=100, fg_color="black")
        self.video_frame.pack(pady=10, padx=20, fill="x")
        self.video_frame.pack_propagate(False)

        # Label dans le frame pour les visualisations (optionnel)
        self.video_label = ctk.CTkLabel(self.video_frame, text="🎵", font=ctk.CTkFont(size=48), text_color="gray")
        self.video_label.pack(expand=True, fill="both")

        self.open_btn = ctk.CTkButton(self, text="Ouvrir un MP3", command=self.open_mp3)
        self.open_btn.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="Aucun fichier sélectionné.")
        self.status_label.pack(pady=5)

        # Contrôles
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=8)

        self.play_btn = ctk.CTkButton(self.control_frame, text="▶", width=50, command=self.play)
        self.play_btn.grid(row=0, column=0, padx=4)

        self.pause_btn = ctk.CTkButton(self.control_frame, text="⏸", width=50, command=self.pause)
        self.pause_btn.grid(row=0, column=1, padx=4)

        self.stop_btn = ctk.CTkButton(self.control_frame, text="⏹", width=50, command=self.stop)
        self.stop_btn.grid(row=0, column=2, padx=4)

        self.time_label = ctk.CTkLabel(self, text="00:00 / 00:00")
        self.time_label.pack(pady=5)

        # Slider de progression
        self.progress_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.seek)
        self.progress_slider.pack(pady=5, fill="x", padx=20)

        # Mise à jour périodique de la progression
        self.update_progress()

    def _create_player(self):
        """Crée l'instance de player VLC avec intégration dans la fenêtre."""
        if self.player is None:
            # Créer l'instance VLC avec les paramètres d'intégration
            self.player = vlc.MediaPlayer()
            
            # Pour Windows - intégrer dans la fenêtre
            if hasattr(self.video_frame, 'winfo_id'):
                self.player.set_xwindow(self.video_frame.winfo_id())
            
            # Note: Pour MP3 seulement, vous pouvez aussi utiliser :
            # self.player.audio_set_volume(100)

    def open_mp3(self):
        """Ouvre un fichier MP3 et prépare la lecture."""
        path = filedialog.askopenfilename(
            title="Sélectionner un fichier MP3", 
            filetypes=[("Fichiers audio", "*.mp3 *.wav *.flac *.m4a"), ("Tous les fichiers", "*.*")]
        )
        if path:
            self.current_file = path
            self.status_label.configure(text=f"Fichier : {os.path.basename(path)}")
            self._create_player()
            media = vlc.Media(self.current_file)
            self.player.set_media(media)
            
            # Mettre à jour le label avec le nom du fichier
            self.video_label.configure(text="🎵 " + os.path.basename(path)[:20] + ("..." if len(os.path.basename(path)) > 20 else ""))
        else:
            self.status_label.configure(text="Aucun fichier sélectionné.")
            self.current_file = None

    def play(self):
        """Démarre ou reprend la lecture."""
        if self.current_file:
            self._create_player()
            if self.player.get_media() is None:
                media = vlc.Media(self.current_file)
                self.player.set_media(media)
            self.player.play()
            self.status_label.configure(text="Lecture en cours...")
            self.video_label.configure(text="🎵 ▶ Lecture...")
        else:
            self.status_label.configure(text="Pas de fichier à lire.")

    def pause(self):
        """Met la lecture en pause."""
        if self.player:
            self.player.pause()
            self.status_label.configure(text="Lecture en pause")
            self.video_label.configure(text="🎵 ⏸ Pause")

    def stop(self):
        """Arrête la lecture."""
        if self.player:
            self.player.stop()
            self.status_label.configure(text="Lecture arrêtée")
            if self.current_file:
                self.video_label.configure(text="🎵 " + os.path.basename(self.current_file)[:20])
            else:
                self.video_label.configure(text="🎵")

    def seek(self, value):
        """Change la position de lecture."""
        if self.player and self.player.get_length() > 0:
            self.player.set_position(value / 100)

    def update_progress(self):
        """Met à jour le slider et le label de temps."""
        if self.player and self.player.is_playing():
            # Mettre à jour le slider
            length = self.player.get_length()
            time = self.player.get_time()
            if length > 0:
                position = (time / length) * 100
                self.progress_slider.set(position)
                
                # Mettre à jour le label de temps
                time_str = self._format_time(time)
                length_str = self._format_time(length)
                self.time_label.configure(text=f"{time_str} / {length_str}")
        
        # Rappeler cette fonction toutes les 500ms
        self.after(500, self.update_progress)

    def _format_time(self, milliseconds):
        """Formate le temps en mm:ss."""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def destroy(self):
        """Nettoie le player à la fermeture."""
        if self.player:
            self.player.stop()
            self.player.release()
        super().destroy()