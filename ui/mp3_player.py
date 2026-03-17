import customtkinter as ctk
from tkinter import filedialog
import vlc
import os
import random
import json
import threading
from pathlib import Path

try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


# ─────────────────────────────────────────────
#  Carte de piste dans la playlist
# ─────────────────────────────────────────────
class TrackCard(ctk.CTkFrame):
    def __init__(self, parent, index, path, on_play, on_remove, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.path = path
        self.index = index

        self.columnconfigure(1, weight=1)

        name = os.path.basename(path)
        short = (name[:28] + "…") if len(name) > 30 else name

        self.num_label = ctk.CTkLabel(self, text=f"{index + 1:02d}", width=28,
                                      font=ctk.CTkFont(size=11), text_color="gray60")
        self.num_label.grid(row=0, column=0, sticky="w", padx=(4, 0))

        self.track_btn = ctk.CTkButton(
            self, text=short, anchor="w", fg_color="transparent",
            hover_color=("gray85", "gray25"), font=ctk.CTkFont(size=12),
            command=lambda: on_play(path)
        )
        self.track_btn.grid(row=0, column=1, sticky="ew", padx=2)

        self.remove_btn = ctk.CTkButton(
            self, text="✕", width=26, height=26, fg_color="transparent",
            hover_color=("gray80", "gray30"), text_color=("gray50", "gray60"),
            font=ctk.CTkFont(size=11), command=lambda: on_remove(path)
        )
        self.remove_btn.grid(row=0, column=2, padx=(0, 4))

    def set_active(self, active: bool):
        if active:
            self.track_btn.configure(
                fg_color=("dodger blue", "#1a6fa8"),
                text_color="white",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            self.num_label.configure(text="▶", text_color="white")
        else:
            self.track_btn.configure(
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                font=ctk.CTkFont(size=12)
            )
            self.num_label.configure(text=f"{self.index + 1:02d}", text_color="gray60")


# ─────────────────────────────────────────────
#  Lecteur principal
# ─────────────────────────────────────────────
class MP3Player(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # ── État ──
        self.player = None
        self.playlist = []
        self.cards = []
        self.current_index = -1
        self.shuffle_mode = False
        self.repeat_mode = "none"   # "none" | "one" | "all"
        self.is_seeking = False
        self._after_id = None

        # ── Mise en page racine ──
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_player_panel()
        self._create_vlc_player()
        self._update_loop()

    # ──────────────────────────────────────────
    #  Sidebar
    # ──────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="🎶 Playlist",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w")

        self.count_label = ctk.CTkLabel(header, text="0 piste",
                                        font=ctk.CTkFont(size=11), text_color="gray60")
        self.count_label.grid(row=0, column=1, sticky="e")

        self.playlist_box = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.playlist_box.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        # Recherche
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._filter_playlist)
        ctk.CTkEntry(self.sidebar, textvariable=self.search_var,
                     placeholder_text="🔍 Rechercher…").grid(
            row=2, column=0, sticky="ew", padx=10, pady=(0, 4))

        btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 4))
        btn_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="➕ Ajouter",
                      command=self.add_to_playlist).grid(row=0, column=0, padx=(0, 3), sticky="ew")
        ctk.CTkButton(btn_frame, text="💾 Sauver",
                      command=self.save_playlist,
                      fg_color=("gray75", "gray30")).grid(row=0, column=1, padx=(3, 0), sticky="ew")

        ctk.CTkButton(self.sidebar, text="📂 Charger playlist",
                      command=self.load_playlist,
                      fg_color=("gray75", "gray30")).grid(
            row=4, column=0, sticky="ew", padx=10, pady=(0, 10))

    # ──────────────────────────────────────────
    #  Panneau lecteur
    # ──────────────────────────────────────────
    def _build_player_panel(self):
        self.player_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.player_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.player_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(self.player_frame, text="MP3 Player Pro",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 10))

        # Pochette + métadonnées
        art_frame = ctk.CTkFrame(self.player_frame, height=160,
                                  fg_color=("gray90", "gray15"), corner_radius=12)
        art_frame.pack(fill="x", pady=(0, 8))
        art_frame.pack_propagate(False)

        self.artwork_label = ctk.CTkLabel(art_frame, text="🎵",
                                           font=ctk.CTkFont(size=64), text_color="gray50")
        self.artwork_label.place(relx=0.12, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(art_frame, fg_color="transparent")
        info_frame.place(relx=0.28, rely=0.5, anchor="w", relwidth=0.68)

        self.title_label = ctk.CTkLabel(info_frame, text="Aucune piste",
                                         font=ctk.CTkFont(size=15, weight="bold"),
                                         anchor="w", wraplength=280)
        self.title_label.pack(anchor="w")

        self.artist_label = ctk.CTkLabel(info_frame, text="",
                                          font=ctk.CTkFont(size=12), text_color="gray60", anchor="w")
        self.artist_label.pack(anchor="w")

        self.album_label = ctk.CTkLabel(info_frame, text="",
                                         font=ctk.CTkFont(size=11), text_color="gray70", anchor="w")
        self.album_label.pack(anchor="w")

        self.status_label = ctk.CTkLabel(info_frame, text="Arrêté",
                                          font=ctk.CTkFont(size=11), text_color="gray55", anchor="w")
        self.status_label.pack(anchor="w", pady=(6, 0))

        # Barre de progression
        time_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=(4, 0))
        time_frame.columnconfigure(1, weight=1)

        self.time_current = ctk.CTkLabel(time_frame, text="00:00",
                                          font=ctk.CTkFont(size=11), width=40)
        self.time_current.grid(row=0, column=0)

        self.progress_slider = ctk.CTkSlider(time_frame, from_=0, to=100,
                                              command=self._on_seek_move)
        self.progress_slider.grid(row=0, column=1, padx=6, sticky="ew")
        self.progress_slider.bind("<ButtonPress-1>",
                                   lambda e: setattr(self, "is_seeking", True))
        self.progress_slider.bind("<ButtonRelease-1>", self._on_seek_release)

        self.time_total = ctk.CTkLabel(time_frame, text="00:00",
                                        font=ctk.CTkFont(size=11), width=40)
        self.time_total.grid(row=0, column=2)

        # Contrôles
        ctrl = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        ctrl.pack(pady=10)

        self.shuffle_btn = ctk.CTkButton(ctrl, text="🔀", width=36, height=36,
                                          fg_color="transparent",
                                          hover_color=("gray80", "gray30"),
                                          command=self.toggle_shuffle)
        self.shuffle_btn.grid(row=0, column=0, padx=4)

        ctk.CTkButton(ctrl, text="⏮", width=44, height=44,
                      command=self.play_previous).grid(row=0, column=1, padx=4)

        self.play_pause_btn = ctk.CTkButton(ctrl, text="▶", width=60, height=60,
                                             font=ctk.CTkFont(size=18),
                                             command=self.toggle_play_pause)
        self.play_pause_btn.grid(row=0, column=2, padx=4)

        ctk.CTkButton(ctrl, text="⏭", width=44, height=44,
                      command=self.play_next).grid(row=0, column=3, padx=4)

        self.repeat_btn = ctk.CTkButton(ctrl, text="🔁", width=36, height=36,
                                         fg_color="transparent",
                                         hover_color=("gray80", "gray30"),
                                         command=self.toggle_repeat)
        self.repeat_btn.grid(row=0, column=4, padx=4)

        ctk.CTkButton(ctrl, text="⏹", width=36, height=36,
                      fg_color=("gray75", "gray35"),
                      command=self.stop).grid(row=0, column=5, padx=4)

        # Volume
        vol_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        vol_frame.pack(fill="x", pady=(4, 0))
        vol_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(vol_frame, text="🔊", width=28).grid(row=0, column=0)
        self.volume_slider = ctk.CTkSlider(vol_frame, from_=0, to=100,
                                            command=self.set_volume)
        self.volume_slider.grid(row=0, column=1, padx=6, sticky="ew")
        self.volume_slider.set(80)

        self.vol_label = ctk.CTkLabel(vol_frame, text="80%", width=38,
                                       font=ctk.CTkFont(size=11))
        self.vol_label.grid(row=0, column=2)

        # Bouton thème
        ctk.CTkButton(self.player_frame, text="🌙 Thème", width=100, height=28,
                      fg_color=("gray75", "gray30"),
                      command=self.toggle_theme).pack(anchor="e", pady=(10, 0))

    # ──────────────────────────────────────────
    #  VLC
    # ──────────────────────────────────────────
    def _create_vlc_player(self):
        if self.player is None:
            self.player = vlc.MediaPlayer()
            self.player.audio_set_volume(80)

    # ──────────────────────────────────────────
    #  Gestion playlist
    # ──────────────────────────────────────────
    def add_to_playlist(self):
        paths = filedialog.askopenfilenames(
            title="Ajouter des fichiers audio",
            filetypes=[("Audio", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac"), ("Tous", "*.*")]
        )
        if paths:
            for path in paths:
                if path not in self.playlist:
                    self.playlist.append(path)
                    self._add_card(path)
            self._update_count()
            if self.current_index == -1:
                self.current_index = 0

    def _add_card(self, path):
        idx = len(self.cards)
        card = TrackCard(self.playlist_box, idx, path,
                         on_play=self.play_specific,
                         on_remove=self.remove_from_playlist)
        card.pack(fill="x", pady=1)
        self.cards.append(card)

    def remove_from_playlist(self, path):
        if path not in self.playlist:
            return
        idx = self.playlist.index(path)
        was_current = (idx == self.current_index)

        if was_current:
            self.stop()

        self.playlist.pop(idx)
        for c in self.cards:
            c.destroy()
        self.cards.clear()
        for p in self.playlist:
            self._add_card(p)

        if was_current:
            self.current_index = min(idx, len(self.playlist) - 1)
        elif idx < self.current_index:
            self.current_index -= 1

        self._refresh_active_card()
        self._update_count()

    def _filter_playlist(self, *_):
        query = self.search_var.get().lower()
        for card in self.cards:
            name = os.path.basename(card.path).lower()
            if query in name:
                card.pack(fill="x", pady=1)
            else:
                card.pack_forget()

    def _update_count(self):
        n = len(self.playlist)
        self.count_label.configure(text=f"{n} piste{'s' if n > 1 else ''}")

    def _refresh_active_card(self):
        for i, card in enumerate(self.cards):
            card.set_active(i == self.current_index)

    # ──────────────────────────────────────────
    #  Sauvegarde / chargement
    # ──────────────────────────────────────────
    def save_playlist(self):
        if not self.playlist:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".m3u",
            filetypes=[("Playlist M3U", "*.m3u"), ("JSON", "*.json")]
        )
        if not path:
            return
        if path.endswith(".json"):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.playlist, f, indent=2)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for p in self.playlist:
                    f.write(p + "\n")

    def load_playlist(self):
        path = filedialog.askopenfilename(
            filetypes=[("Playlist", "*.m3u *.json"), ("Tous", "*.*")]
        )
        if not path:
            return
        paths = []
        if path.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                paths = json.load(f)
        else:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and os.path.exists(line):
                        paths.append(line)
        for p in paths:
            if p not in self.playlist:
                self.playlist.append(p)
                self._add_card(p)
        self._update_count()
        if self.current_index == -1 and self.playlist:
            self.current_index = 0

    # ──────────────────────────────────────────
    #  Métadonnées (mutagen)
    # ──────────────────────────────────────────
    def _load_metadata(self, path):
        title = os.path.splitext(os.path.basename(path))[0]
        artist, album = "", ""

        if MUTAGEN_AVAILABLE:
            try:
                audio = MutagenFile(path, easy=True)
                if audio:
                    title = str(audio.get("title", [title])[0])
                    artist = str(audio.get("artist", [""])[0])
                    album = str(audio.get("album", [""])[0])
            except Exception:
                pass

        self.title_label.configure(text=title[:45])
        self.artist_label.configure(text=artist)
        self.album_label.configure(text=album)

    # ──────────────────────────────────────────
    #  Lecture / contrôle
    # ──────────────────────────────────────────
    def play_specific(self, path):
        if path in self.playlist:
            self.current_index = self.playlist.index(path)
            self._load_and_play()

    def _load_and_play(self):
        if not (0 <= self.current_index < len(self.playlist)):
            return
        file_path = self.playlist[self.current_index]
        if not os.path.exists(file_path):
            self.status_label.configure(text="⚠ Fichier introuvable")
            return

        def _do():
            media = vlc.Media(file_path)
            self.player.set_media(media)
            self.player.play()

        threading.Thread(target=_do, daemon=True).start()
        self._load_metadata(file_path)
        self.status_label.configure(text="⏳ Chargement…")
        self.play_pause_btn.configure(text="⏸")
        self._refresh_active_card()

    def toggle_play_pause(self):
        if not self.player:
            return
        state = self.player.get_state()
        if state == vlc.State.Playing:
            self.player.pause()
            self.play_pause_btn.configure(text="▶")
            self.status_label.configure(text="En pause")
        elif state == vlc.State.Paused:
            self.player.play()
            self.play_pause_btn.configure(text="⏸")
            self.status_label.configure(text="▶ Lecture")
        else:
            if self.current_index == -1 and self.playlist:
                self.current_index = 0
            if 0 <= self.current_index < len(self.playlist):
                self._load_and_play()

    def stop(self):
        if self.player:
            self.player.stop()
        self.play_pause_btn.configure(text="▶")
        self.status_label.configure(text="Arrêté")
        self.progress_slider.set(0)
        self.time_current.configure(text="00:00")

    def play_next(self):
        if not self.playlist:
            return
        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self._load_and_play()

    def play_previous(self):
        if not self.playlist:
            return
        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self._load_and_play()

    def toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        self.shuffle_btn.configure(
            fg_color=("dodger blue", "#1a6fa8") if self.shuffle_mode else "transparent")

    def toggle_repeat(self):
        modes = ["none", "all", "one"]
        icons = {"none": "🔁", "all": "🔁", "one": "🔂"}
        colors = {"none": "transparent", "all": ("dodger blue", "#1a6fa8"),
                  "one": ("dodger blue", "#1a6fa8")}
        self.repeat_mode = modes[(modes.index(self.repeat_mode) + 1) % len(modes)]
        self.repeat_btn.configure(text=icons[self.repeat_mode],
                                   fg_color=colors[self.repeat_mode])

    def set_volume(self, value):
        if self.player:
            self.player.audio_set_volume(int(value))
        self.vol_label.configure(text=f"{int(value)}%")

    def increase_volume(self, step=10):
        v = min(100, self.volume_slider.get() + step)
        self.volume_slider.set(v)
        self.set_volume(v)

    def decrease_volume(self, step=10):
        v = max(0, self.volume_slider.get() - step)
        self.volume_slider.set(v)
        self.set_volume(v)

    def _on_seek_move(self, value):
        if self.player:
            length = self.player.get_length()
            if length > 0:
                ms = int((float(value) / 100) * length)
                self.time_current.configure(text=self._fmt(ms))

    def _on_seek_release(self, _event):
        if self.player and self.player.get_length() > 0:
            self.player.set_position(self.progress_slider.get() / 100)
        self.is_seeking = False

    # ──────────────────────────────────────────
    #  Boucle de mise à jour (500 ms)
    # ──────────────────────────────────────────
    def _update_loop(self):
        if self.player:
            state = self.player.get_state()

            if state == vlc.State.Playing:
                self.status_label.configure(text="▶ Lecture")
                self.play_pause_btn.configure(text="⏸")
                if not self.is_seeking:
                    length = self.player.get_length()
                    time_ms = self.player.get_time()
                    if length > 0:
                        self.progress_slider.set((time_ms / length) * 100)
                        self.time_current.configure(text=self._fmt(time_ms))
                        self.time_total.configure(text=self._fmt(length))

            elif state == vlc.State.Paused:
                self.play_pause_btn.configure(text="▶")

            elif state == vlc.State.Ended:
                if self.repeat_mode == "one":
                    self._load_and_play()
                elif self.repeat_mode == "all" or self.shuffle_mode:
                    self.play_next()
                elif self.current_index < len(self.playlist) - 1:
                    self.play_next()
                else:
                    self.stop()

        self._after_id = self.after(400, self._update_loop)

    # ──────────────────────────────────────────
    #  Thème
    # ──────────────────────────────────────────
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")

    # ──────────────────────────────────────────
    #  Utilitaires
    # ──────────────────────────────────────────
    @staticmethod
    def _fmt(ms: int) -> str:
        s = max(0, ms // 1000)
        return f"{s // 60:02d}:{s % 60:02d}"

    def destroy(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        if self.player:
            self.player.stop()
            self.player.release()
        super().destroy()


# ─────────────────────────────────────────────
#  Lancement
# ─────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("MP3 Player Pro")
    root.geometry("920x560")
    root.minsize(700, 480)

    player = MP3Player(root)
    player.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", lambda: (player.destroy(), root.destroy()))
    root.mainloop()
