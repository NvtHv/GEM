import customtkinter as ctk
from tkinter import filedialog
import vlc
import os
import threading

try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


class MP4Player(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # ── État ──
        self.instance = None
        self.player = None
        self.current_file = None
        self.is_playing = False
        self.is_seeking = False
        self._after_id = None
        self._fullscreen = False

        # ── Layout racine ──
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_topbar()
        self._build_video_area()
        self._build_controls()
        self._build_bottombar()

        # Raccourcis clavier
        parent.bind("<space>", lambda e: self.toggle_play_pause())
        parent.bind("<Left>",  lambda e: self._skip(-5000))
        parent.bind("<Right>", lambda e: self._skip(5000))
        parent.bind("<Up>",    lambda e: self.increase_volume())
        parent.bind("<Down>",  lambda e: self.decrease_volume())
        parent.bind("<f>",     lambda e: self.toggle_fullscreen())

        self.after(400, self._setup_player)
        self._update_loop()

    # ──────────────────────────────────────────
    #  Construction UI
    # ──────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        bar.columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text="📽️ Lecteur Vidéo",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w")

        self.title_label = ctk.CTkLabel(bar, text="",
                                         font=ctk.CTkFont(size=13), text_color="gray60")
        self.title_label.grid(row=0, column=1, sticky="w", padx=12)

        ctk.CTkButton(bar, text="🌙 Thème", width=90, height=28,
                      fg_color=("gray75", "gray30"),
                      command=self.toggle_theme).grid(row=0, column=2, sticky="e")

    def _build_video_area(self):
        self.video_frame = ctk.CTkFrame(self, fg_color="black", corner_radius=8)
        self.video_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        self.video_frame.pack_propagate(False)
        self.video_frame.configure(width=640, height=360)

        self.placeholder_label = ctk.CTkLabel(
            self.video_frame, text="🎬  Aucune vidéo chargée",
            font=ctk.CTkFont(size=22), text_color="gray40"
        )
        self.placeholder_label.pack(expand=True)

        # Double-clic → plein écran
        self.video_frame.bind("<Double-Button-1>", lambda e: self.toggle_fullscreen())

    def _build_controls(self):
        ctrl_wrap = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_wrap.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 4))
        ctrl_wrap.columnconfigure(0, weight=1)

        # ── Barre de progression ──
        time_row = ctk.CTkFrame(ctrl_wrap, fg_color="transparent")
        time_row.pack(fill="x")
        time_row.columnconfigure(1, weight=1)

        self.time_current = ctk.CTkLabel(time_row, text="00:00", width=44,
                                          font=ctk.CTkFont(size=11))
        self.time_current.grid(row=0, column=0)

        self.progress_slider = ctk.CTkSlider(time_row, from_=0, to=100,
                                              command=self._on_seek_move)
        self.progress_slider.grid(row=0, column=1, padx=6, sticky="ew")
        self.progress_slider.set(0)
        self.progress_slider.bind("<ButtonPress-1>",
                                   lambda e: setattr(self, "is_seeking", True))
        self.progress_slider.bind("<ButtonRelease-1>", self._on_seek_release)

        self.time_total = ctk.CTkLabel(time_row, text="00:00", width=44,
                                        font=ctk.CTkFont(size=11))
        self.time_total.grid(row=0, column=2)

        # ── Boutons ──
        btn_row = ctk.CTkFrame(ctrl_wrap, fg_color="transparent")
        btn_row.pack(pady=6)

        ctk.CTkButton(btn_row, text="⏮", width=38, height=38,
                      fg_color=("gray75", "gray35"),
                      command=lambda: self._skip(-10000)).grid(row=0, column=0, padx=3)

        ctk.CTkButton(btn_row, text="◀◀ 5s", width=54, height=38,
                      fg_color=("gray75", "gray35"),
                      command=lambda: self._skip(-5000)).grid(row=0, column=1, padx=3)

        self.play_pause_btn = ctk.CTkButton(btn_row, text="▶", width=64, height=48,
                                             font=ctk.CTkFont(size=18),
                                             command=self.toggle_play_pause)
        self.play_pause_btn.grid(row=0, column=2, padx=3)

        ctk.CTkButton(btn_row, text="5s ▶▶", width=54, height=38,
                      fg_color=("gray75", "gray35"),
                      command=lambda: self._skip(5000)).grid(row=0, column=3, padx=3)

        ctk.CTkButton(btn_row, text="⏭", width=38, height=38,
                      fg_color=("gray75", "gray35"),
                      command=lambda: self._skip(10000)).grid(row=0, column=4, padx=3)

        ctk.CTkButton(btn_row, text="⏹", width=38, height=38,
                      fg_color=("gray75", "gray35"),
                      command=self.stop).grid(row=0, column=5, padx=3)

        self.fullscreen_btn = ctk.CTkButton(btn_row, text="⛶", width=38, height=38,
                                             fg_color=("gray75", "gray35"),
                                             command=self.toggle_fullscreen)
        self.fullscreen_btn.grid(row=0, column=6, padx=3)

    def _build_bottombar(self):
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 10))
        bottom.columnconfigure(2, weight=1)

        # Bouton ouvrir
        ctk.CTkButton(bottom, text="📂 Ouvrir",
                      command=self.open_file).grid(row=0, column=0, padx=(0, 8))

        # Vitesse de lecture
        ctk.CTkLabel(bottom, text="Vitesse :").grid(row=0, column=1, padx=(0, 4))
        self.speed_menu = ctk.CTkOptionMenu(
            bottom, values=["0.25×", "0.5×", "0.75×", "1×", "1.25×", "1.5×", "2×"],
            width=80, command=self._set_speed
        )
        self.speed_menu.set("1×")
        self.speed_menu.grid(row=0, column=2, sticky="w", padx=(0, 12))

        # Volume
        ctk.CTkLabel(bottom, text="🔊", width=28).grid(row=0, column=3)
        self.volume_slider = ctk.CTkSlider(bottom, from_=0, to=100,
                                            width=130, command=self.set_volume)
        self.volume_slider.set(80)
        self.volume_slider.grid(row=0, column=4, padx=4)

        self.vol_label = ctk.CTkLabel(bottom, text="80%", width=36,
                                       font=ctk.CTkFont(size=11))
        self.vol_label.grid(row=0, column=5)

        # Status
        self.status_label = ctk.CTkLabel(bottom, text="Aucun fichier sélectionné.",
                                          font=ctk.CTkFont(size=11), text_color="gray60")
        self.status_label.grid(row=1, column=0, columnspan=6, sticky="w", pady=(4, 0))

    # ──────────────────────────────────────────
    #  VLC
    # ──────────────────────────────────────────
    def _setup_player(self):
        try:
            self.instance = vlc.Instance("--quiet")
            self.player = self.instance.media_player_new()
            self.player.audio_set_volume(80)

            wid = self.video_frame.winfo_id()
            if os.name == "nt":
                self.player.set_hwnd(wid)
            else:
                self.player.set_xwindow(wid)
        except Exception as e:
            self.status_label.configure(text=f"⚠ Erreur VLC : {e}")

    # ──────────────────────────────────────────
    #  Ouverture
    # ──────────────────────────────────────────
    def open_file(self):
        path = filedialog.askopenfilename(
            title="Ouvrir une vidéo",
            filetypes=[("Vidéo", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                       ("Tous", "*.*")]
        )
        if path:
            self._load(path)

    def _load(self, path):
        if not self.player:
            return
        if not os.path.exists(path):
            self.status_label.configure(text="⚠ Fichier introuvable")
            return

        self.current_file = path
        self.placeholder_label.pack_forget()

        def _do():
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.player.play()

        threading.Thread(target=_do, daemon=True).start()

        name = os.path.basename(path)
        self.title_label.configure(text=name)
        self.status_label.configure(text=f"▶ {name}")
        self.play_pause_btn.configure(text="⏸")
        self.is_playing = True

    # ──────────────────────────────────────────
    #  Contrôles lecture
    # ──────────────────────────────────────────
    def toggle_play_pause(self):
        if not self.player or not self.player.get_media():
            return
        if self.player.is_playing():
            self.player.pause()
            self.play_pause_btn.configure(text="▶")
            self.is_playing = False
            self.status_label.configure(text="⏸ En pause")
        else:
            self.player.play()
            self.play_pause_btn.configure(text="⏸")
            self.is_playing = True
            self.status_label.configure(text=f"▶ {os.path.basename(self.current_file or '')}")

    def stop(self):
        if self.player:
            self.player.stop()
        self.play_pause_btn.configure(text="▶")
        self.is_playing = False
        self.progress_slider.set(0)
        self.time_current.configure(text="00:00")
        self.status_label.configure(text="⏹ Arrêté")

    def _skip(self, ms: int):
        """Avance / recule de ms millisecondes."""
        if self.player and self.player.get_length() > 0:
            new_time = max(0, min(self.player.get_time() + ms,
                                   self.player.get_length()))
            self.player.set_time(new_time)

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

    def _set_speed(self, label: str):
        if self.player:
            rate = float(label.replace("×", ""))
            self.player.set_rate(rate)

    # ──────────────────────────────────────────
    #  Seek
    # ──────────────────────────────────────────
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
    #  Plein écran
    # ──────────────────────────────────────────
    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        root = self.winfo_toplevel()
        root.attributes("-fullscreen", self._fullscreen)
        self.fullscreen_btn.configure(
            text="✕ Quitter" if self._fullscreen else "⛶"
        )
        if self._fullscreen:
            root.bind("<Escape>", lambda e: self.toggle_fullscreen())

    # ──────────────────────────────────────────
    #  Boucle de mise à jour
    # ──────────────────────────────────────────
    def _update_loop(self):
        if self.player:
            state = self.player.get_state()

            if state == vlc.State.Playing:
                self.play_pause_btn.configure(text="⏸")
                if not self.is_seeking:
                    length = self.player.get_length()
                    t = self.player.get_time()
                    if length > 0:
                        self.progress_slider.set((t / length) * 100)
                        self.time_current.configure(text=self._fmt(t))
                        self.time_total.configure(text=self._fmt(length))

            elif state == vlc.State.Paused:
                self.play_pause_btn.configure(text="▶")

            elif state == vlc.State.Ended:
                self.stop()

        self._after_id = self.after(400, self._update_loop)

    # ──────────────────────────────────────────
    #  Thème
    # ──────────────────────────────────────────
    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if mode == "Dark" else "Dark")

    # ──────────────────────────────────────────
    #  Utilitaires
    # ──────────────────────────────────────────
    @staticmethod
    def _fmt(ms: int) -> str:
        s = max(0, ms // 1000)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"

    def destroy(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        if self.player:
            self.player.stop()
            self.player.release()
        if self.instance:
            self.instance.release()
        super().destroy()


# ─────────────────────────────────────────────
#  Lancement
# ─────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Lecteur Vidéo Pro")
    root.geometry("800x620")
    root.minsize(640, 500)

    player = MP4Player(root)
    player.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", lambda: (player.destroy(), root.destroy()))
    root.mainloop()
