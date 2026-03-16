import customtkinter as ctk
from tkinter import filedialog
import vlc
import os
import tkinter as tk


class MP4Player(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.player = None
        self.current_file = None
        self.video_panel = None

        # Titre
        self.label = ctk.CTkLabel(self, text="📽️ Lecteur MP4", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=10)

        # Frame pour la vidéo (zone d'affichage)
        self.video_frame = ctk.CTkFrame(self, width=640, height=360, fg_color="black")
        self.video_frame.pack(pady=10, padx=10)
        self.video_frame.pack_propagate(False)

        # Label de placeholder (quand aucune vidéo)
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
        self.volume_slider.set(80)  # Volume à 80% par défaut

        # Mise à jour périodique de la progression
        self.update_progress()

    def _create_player(self):
        """Crée l'instance de player VLC avec intégration vidéo."""
        if self.player is None:
            # Créer l'instance VLC avec les paramètres d'intégration
            self.player = vlc.MediaPlayer()
            
            # Cacher le placeholder
            self.placeholder_label.pack_forget()
            
            # Intégrer la vidéo dans le frame selon l'OS
            if os.name == 'nt':  # Windows
                self.player.set_hwnd(self.video_frame.winfo_id())
            else:  # Linux/Mac
                self.player.set_xwindow(self.video_frame.winfo_id())

    def open_mp4(self):
        """Ouvre un fichier MP4 et prépare la lecture."""
        path = filedialog.askopenfilename(
            title="Sélectionner un fichier MP4", 
            filetypes=[("Fichiers vidéo", "*.mp4 *.avi *.mkv *.mov"), ("Tous les fichiers", "*.*")]
        )
        if path:
            self.current_file = path
            filename = os.path.basename(path)
            self.status_label.configure(text=f"Fichier : {filename[:30]}{'...' if len(filename) > 30 else ''}")
            
            self._create_player()
            media = vlc.Media(self.current_file)
            self.player.set_media(media)
            
            # Mettre à jour le titre
            self.label.configure(text=f"📽️ {filename[:20]}{'...' if len(filename) > 20 else ''}")
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
            self.status_label.configure(text="▶ Lecture en cours...")
        else:
            self.status_label.configure(text="❌ Pas de fichier à lire.")

    def pause(self):
        """Met la lecture en pause."""
        if self.player:
            self.player.pause()
            self.status_label.configure(text="⏸ Lecture en pause")

    def stop(self):
        """Arrête la lecture et remet à zéro."""
        if self.player:
            self.player.stop()
            self.status_label.configure(text="⏹ Lecture arrêtée")
            self.progress_slider.set(0)
            self.time_label.configure(text="00:00 / 00:00")

    def seek(self, value):
        """Change la position de lecture."""
        if self.player and self.player.get_length() > 0:
            self.player.set_position(value / 100)

    def set_volume(self, value):
        """Règle le volume."""
        if self.player:
            self.player.audio_set_volume(int(value))
            # Changer l'icône selon le volume
            if value == 0:
                self.volume_label.configure(text="🔇")
            elif value < 30:
                self.volume_label.configure(text="🔈")
            elif value < 70:
                self.volume_label.configure(text="🔉")
            else:
                self.volume_label.configure(text="🔊")

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
        hours = minutes // 60
        if hours > 0:
            minutes = minutes % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def destroy(self):
        """Nettoie le player à la fermeture."""
        if self.player:
            self.player.stop()
            self.player.release()
        super().destroy()