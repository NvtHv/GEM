import customtkinter as ctk
from tkinter import filedialog
import vlc
import os

class MP3Player(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # --- Variables d'état ---
        self.player = None
        self.playlist = []  # Liste des chemins complets des fichiers
        self.current_index = -1
        
        # --- Configuration de la Grille ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANNEAU GAUCHE : LISTE DE LECTURE ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        ctk.CTkLabel(self.sidebar, text="🎶 Ma Playlist", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Zone scrollable pour les titres
        self.playlist_box = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.playlist_box.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.add_btn = ctk.CTkButton(self.sidebar, text="➕ Ajouter des musiques", command=self.add_to_playlist)
        self.add_btn.pack(pady=10, padx=10, fill="x")

        # --- PANNEAU DROIT : LECTEUR ET CONTRÔLES ---
        self.player_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.player_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.label = ctk.CTkLabel(self.player_frame, text="MP3 Player", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=10)

        # Zone visuelle (Pochette / Logo)
        self.video_frame = ctk.CTkFrame(self.player_frame, width=400, height=150, fg_color="black")
        self.video_frame.pack(pady=10, fill="x")
        self.video_frame.pack_propagate(False)

        self.video_label = ctk.CTkLabel(self.video_frame, text="🎵", font=ctk.CTkFont(size=64), text_color="gray")
        self.video_label.pack(expand=True, fill="both")

        self.status_label = ctk.CTkLabel(self.player_frame, text="Aucun fichier sélectionné.")
        self.status_label.pack(pady=5)

        # Boutons de contrôle
        self.control_frame = ctk.CTkFrame(self.player_frame)
        self.control_frame.pack(pady=10)

        self.prev_btn = ctk.CTkButton(self.control_frame, text="⏮", width=40, command=self.play_previous)
        self.prev_btn.grid(row=0, column=0, padx=5)
        
        self.play_btn = ctk.CTkButton(self.control_frame, text="▶", width=60, command=self.play)
        self.play_btn.grid(row=0, column=1, padx=5)

        self.pause_btn = ctk.CTkButton(self.control_frame, text="⏸", width=60, command=self.pause)
        self.pause_btn.grid(row=0, column=2, padx=5)

        self.next_btn = ctk.CTkButton(self.control_frame, text="⏭", width=40, command=self.play_next)
        self.next_btn.grid(row=0, column=3, padx=5)

        self.stop_btn = ctk.CTkButton(self.control_frame, text="⏹", width=40, command=self.stop)
        self.stop_btn.grid(row=0, column=4, padx=5)

        self.clear_btn = ctk.CTkButton(
            self.sidebar, 
            text="🗑️ Vider la playlist", 
            command=self.clear_playlist,
            fg_color="#A12222",  # Couleur rouge pour indiquer une action de suppression
            hover_color="#7A1A1A"
        )
        self.clear_btn.pack(pady=5, padx=10, fill="x")

        # Temps et Barres de progression
        self.time_label = ctk.CTkLabel(self.player_frame, text="00:00 / 00:00")
        self.time_label.pack()

        self.progress_slider = ctk.CTkSlider(self.player_frame, from_=0, to=100, command=self.seek)
        self.progress_slider.pack(pady=10, fill="x")

        self.volume_label = ctk.CTkLabel(self.player_frame, text="Volume")
        self.volume_label.pack()
        self.volume_slider = ctk.CTkSlider(self.player_frame, from_=0, to=100, command=self.set_volume)
        self.volume_slider.pack(pady=5, fill="x")
        self.volume_slider.set(80)

        # Initialisation du player VLC
        self._create_player()
        self.update_progress()
    
    def clear_playlist(self):
        """Arrête la lecture et vide la liste de lecture."""
        # 1. Arrêter la musique
        self.stop()
        
        # 2. Réinitialiser les variables
        self.playlist = []
        self.current_index = -1
        
        # 3. Nettoyer visuellement la sidebar (supprimer les boutons)
        for widget in self.playlist_box.winfo_children():
            widget.destroy()
            
        # 4. Mettre à jour l'interface
        self.status_label.configure(text="Playlist vidée.")
        self.video_label.configure(image="", text="🎵")
        self.time_label.configure(text="00:00 / 00:00")
        self.progress_slider.set(0)


    def _create_player(self):
        """Initialise l'instance VLC."""
        if self.player is None:
            self.player = vlc.MediaPlayer()
            # Intégration optionnelle dans le cadre vidéo
            if hasattr(self.video_frame, 'winfo_id'):
                self.player.set_xwindow(self.video_frame.winfo_id())

    def add_to_playlist(self):
        """Ouvre une boîte de dialogue pour ajouter plusieurs musiques."""
        paths = filedialog.askopenfilenames(
            title="Ajouter des musiques", 
            filetypes=[("Fichiers Audio", "*.mp3 *.wav *.flac *.m4a"), ("Tous les fichiers", "*.*")]
        )
        if paths:
            for path in paths:
                self.playlist.append(path)
                # Créer un bouton cliquable pour chaque musique dans la sidebar
                btn = ctk.CTkButton(
                    self.playlist_box, 
                    text=os.path.basename(path)[:30], 
                    fg_color="transparent", 
                    anchor="w",
                    command=lambda p=path: self.play_specific(p)
                )
                btn.pack(fill="x", pady=1)
            
            if self.current_index == -1:
                self.current_index = 0
                self.status_label.configure(text=f"{len(self.playlist)} musiques dans la liste.")

    def play_specific(self, path):
        """Lance une musique spécifique de la playlist."""
        self.current_index = self.playlist.index(path)
        self.load_and_play()

    def load_and_play(self):
        """Charge le fichier actuel et lance la lecture."""
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            media = vlc.Media(file_path)
            self.player.set_media(media)
            self.player.play()
            
            filename = os.path.basename(file_path)
            self.status_label.configure(text=f"Lecture : {filename}")
            self.video_label.configure(text="🎵 " + filename[:15] + "...")

    def play(self):
        """Reprend la lecture ou lance la première musique."""
        if self.playlist and self.player.get_media() is None:
            self.load_and_play()
        else:
            self.player.play()

    def pause(self):
        """Met en pause."""
        if self.player:
            self.player.pause()

    def stop(self):
        """Arrête la lecture."""
        if self.player:
            self.player.stop()

    def play_next(self):
        """Musique suivante."""
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.load_and_play()

    def play_previous(self):
        """Musique précédente."""
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.load_and_play()

    def set_volume(self, value):
        """Ajuste le volume."""
        if self.player:
            self.player.audio_set_volume(int(value))

    def seek(self, value):
        """Navigue dans le temps du morceau."""
        if self.player and self.player.get_length() > 0:
            self.player.set_position(value / 100)

    def update_progress(self):
        """Boucle de mise à jour de l'interface (500ms)."""
        if self.player:
            # Vérification de la fin du morceau pour lecture automatique
            if self.player.get_state() == vlc.State.Ended:
                self.play_next()

            if self.player.is_playing():
                length = self.player.get_length()
                time = self.player.get_time()
                if length > 0:
                    self.progress_slider.set((time / length) * 100)
                    self.time_label.configure(text=f"{self._format_time(time)} / {self._format_time(length)}")
        
        self.after(500, self.update_progress)

    def _format_time(self, ms):
        """Formate les millisecondes en mm:ss."""
        s = max(0, ms // 1000)
        return f"{s // 60:02d}:{s % 60:02d}"

    def destroy(self):
        """Libère les ressources VLC à la fermeture."""
        if self.player:
            self.player.stop()
            self.player.release()
        super().destroy()
