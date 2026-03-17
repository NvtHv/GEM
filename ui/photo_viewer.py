import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os


class PhotoViewer(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # ── État ──
        self.current_file = None
        self.original_image = None   # image originale intacte
        self.current_image = None    # image avec transformations
        self.photo_image = None
        self.zoom_factor = 1.0
        self.rotation = 0
        self._history = []           # undo stack
        self._flip_h = False
        self._flip_v = False

        # ── Layout ──
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_topbar()
        self._build_canvas_area()
        self._build_toolbar()
        self._build_bottombar()

        # Raccourcis clavier
        parent.bind("<plus>",       lambda e: self.zoom_in())
        parent.bind("<minus>",      lambda e: self.zoom_out())
        parent.bind("<r>",          lambda e: self.rotate(90))
        parent.bind("<z>",          lambda e: self.undo())
        parent.bind("<Control-z>",  lambda e: self.undo())
        parent.bind("<Control-o>",  lambda e: self.open_image())
        parent.bind("<Control-s>",  lambda e: self.save_image())
        parent.bind("<Left>",       lambda e: self._nav(-1))
        parent.bind("<Right>",      lambda e: self._nav(1))
        parent.bind("<f>",          lambda e: self.toggle_fullscreen())

        self._fullscreen = False

    # ──────────────────────────────────────────
    #  Construction UI
    # ──────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        bar.columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text="🖼️ Photo Viewer",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w")

        self.file_label = ctk.CTkLabel(bar, text="Aucune image sélectionnée.",
                                        font=ctk.CTkFont(size=11), text_color="gray60")
        self.file_label.grid(row=0, column=1, sticky="w", padx=12)

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e")

        ctk.CTkButton(right, text="🌙 Thème", width=90, height=28,
                      fg_color=("gray75", "gray30"),
                      command=self.toggle_theme).pack(side="left", padx=4)

        ctk.CTkButton(right, text="⛶ Plein écran", width=110, height=28,
                      fg_color=("gray75", "gray30"),
                      command=self.toggle_fullscreen).pack(side="left", padx=4)

    def _build_canvas_area(self):
        self.image_frame = ctk.CTkFrame(self, fg_color=("gray85", "#1a1a2e"), corner_radius=10)
        self.image_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)

        self.image_label = ctk.CTkLabel(self.image_frame, text="📂  Ouvrez une image (Ctrl+O)",
                                         font=ctk.CTkFont(size=18), text_color="gray50")
        self.image_label.pack(expand=True, fill="both")

        # Molette souris → zoom
        self.image_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.image_label.bind("<MouseWheel>", self._on_mousewheel)

    def _build_toolbar(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 4))

        # ── Fichier ──
        file_grp = ctk.CTkFrame(tb)
        file_grp.pack(side="left", padx=(0, 8))

        ctk.CTkButton(file_grp, text="📂 Ouvrir", width=80,
                      command=self.open_image).grid(row=0, column=0, padx=3, pady=4)
        ctk.CTkButton(file_grp, text="💾 Sauver", width=80,
                      fg_color=("gray75", "gray30"),
                      command=self.save_image).grid(row=0, column=1, padx=3, pady=4)
        ctk.CTkButton(file_grp, text="↩ Undo", width=70,
                      fg_color=("gray75", "gray30"),
                      command=self.undo).grid(row=0, column=2, padx=3, pady=4)
        ctk.CTkButton(file_grp, text="🔄 Reset", width=70,
                      fg_color=("gray75", "gray30"),
                      command=self.reset_image).grid(row=0, column=3, padx=3, pady=4)

        # ── Zoom ──
        zoom_grp = ctk.CTkFrame(tb)
        zoom_grp.pack(side="left", padx=8)

        ctk.CTkButton(zoom_grp, text="🔍+", width=44, command=self.zoom_in).grid(row=0, column=0, padx=2, pady=4)
        self.zoom_label = ctk.CTkLabel(zoom_grp, text="100%", width=46,
                                        font=ctk.CTkFont(size=11))
        self.zoom_label.grid(row=0, column=1, padx=2)
        ctk.CTkButton(zoom_grp, text="🔍-", width=44, command=self.zoom_out).grid(row=0, column=2, padx=2, pady=4)
        ctk.CTkButton(zoom_grp, text="⊡ Fit", width=54,
                      fg_color=("gray75", "gray30"),
                      command=self.zoom_fit).grid(row=0, column=3, padx=2, pady=4)

        # ── Rotation / flip ──
        rot_grp = ctk.CTkFrame(tb)
        rot_grp.pack(side="left", padx=8)

        ctk.CTkButton(rot_grp, text="↺ 90°", width=60,
                      command=lambda: self.rotate(-90)).grid(row=0, column=0, padx=2, pady=4)
        ctk.CTkButton(rot_grp, text="↻ 90°", width=60,
                      command=lambda: self.rotate(90)).grid(row=0, column=1, padx=2, pady=4)
        ctk.CTkButton(rot_grp, text="↔ Flip H", width=70,
                      fg_color=("gray75", "gray30"),
                      command=self.flip_horizontal).grid(row=0, column=2, padx=2, pady=4)
        ctk.CTkButton(rot_grp, text="↕ Flip V", width=70,
                      fg_color=("gray75", "gray30"),
                      command=self.flip_vertical).grid(row=0, column=3, padx=2, pady=4)

        # ── Filtres ──
        filt_grp = ctk.CTkFrame(tb)
        filt_grp.pack(side="left", padx=8)

        ctk.CTkLabel(filt_grp, text="Filtre :",
                     font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=(4, 2))
        self.filter_menu = ctk.CTkOptionMenu(
            filt_grp,
            values=["Aucun", "N&B", "Sépia", "Flou", "Netteté", "Contours"],
            width=100,
            command=self.apply_filter
        )
        self.filter_menu.set("Aucun")
        self.filter_menu.grid(row=0, column=1, padx=4, pady=4)

        # ── Réglages ──
        adj_grp = ctk.CTkFrame(tb)
        adj_grp.pack(side="left", padx=8)

        ctk.CTkLabel(adj_grp, text="Luminosité",
                     font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=4)
        self.brightness_slider = ctk.CTkSlider(adj_grp, from_=0.2, to=3.0, width=90,
                                                command=self._apply_adjustments)
        self.brightness_slider.set(1.0)
        self.brightness_slider.grid(row=1, column=0, padx=4, pady=(0, 4))

        ctk.CTkLabel(adj_grp, text="Contraste",
                     font=ctk.CTkFont(size=10)).grid(row=0, column=1, padx=4)
        self.contrast_slider = ctk.CTkSlider(adj_grp, from_=0.2, to=3.0, width=90,
                                              command=self._apply_adjustments)
        self.contrast_slider.set(1.0)
        self.contrast_slider.grid(row=1, column=1, padx=4, pady=(0, 4))

        ctk.CTkLabel(adj_grp, text="Saturation",
                     font=ctk.CTkFont(size=10)).grid(row=0, column=2, padx=4)
        self.saturation_slider = ctk.CTkSlider(adj_grp, from_=0.0, to=3.0, width=90,
                                                command=self._apply_adjustments)
        self.saturation_slider.set(1.0)
        self.saturation_slider.grid(row=1, column=2, padx=4, pady=(0, 4))

    def _build_bottombar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))
        bar.columnconfigure(1, weight=1)

        # Navigation dossier
        nav = ctk.CTkFrame(bar, fg_color="transparent")
        nav.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(nav, text="◀ Précédente", width=110, height=28,
                      fg_color=("gray75", "gray30"),
                      command=lambda: self._nav(-1)).pack(side="left", padx=4)
        ctk.CTkButton(nav, text="Suivante ▶", width=110, height=28,
                      fg_color=("gray75", "gray30"),
                      command=lambda: self._nav(1)).pack(side="left", padx=4)

        self.nav_label = ctk.CTkLabel(bar, text="",
                                       font=ctk.CTkFont(size=11), text_color="gray60")
        self.nav_label.grid(row=0, column=1, sticky="w", padx=8)

        self.info_label = ctk.CTkLabel(bar, text="",
                                        font=ctk.CTkFont(size=11), text_color="gray60")
        self.info_label.grid(row=0, column=2, sticky="e")

    # ──────────────────────────────────────────
    #  Ouverture / navigation
    # ──────────────────────────────────────────
    def open_image(self):
        path = filedialog.askopenfilename(
            title="Ouvrir une image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
                ("Tous", "*.*")
            ]
        )
        if path:
            self._load(path)

    def _load(self, path):
        if not os.path.exists(path):
            return
        try:
            self.current_file = path
            img = Image.open(path).convert("RGBA")
            self.original_image = img.copy()
            self.current_image = img.copy()
            self._history.clear()
            self.zoom_factor = 1.0
            self.rotation = 0
            self._flip_h = False
            self._flip_v = False
            self.brightness_slider.set(1.0)
            self.contrast_slider.set(1.0)
            self.saturation_slider.set(1.0)
            self.filter_menu.set("Aucun")

            name = os.path.basename(path)
            self.file_label.configure(text=name)
            w, h = img.size
            self.info_label.configure(text=f"{w} × {h} px  •  {self._file_size(path)}")
            self._update_nav_label()
            self._display_image()
        except Exception as e:
            self.file_label.configure(text=f"⚠ Erreur : {e}")

    def _nav(self, direction: int):
        if not self.current_file:
            return
        folder = os.path.dirname(self.current_file)
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}
        files = sorted([f for f in os.listdir(folder)
                        if os.path.splitext(f)[1].lower() in exts])
        if not files:
            return
        current_name = os.path.basename(self.current_file)
        try:
            idx = files.index(current_name)
        except ValueError:
            idx = 0
        new_idx = (idx + direction) % len(files)
        self._load(os.path.join(folder, files[new_idx]))

    def _update_nav_label(self):
        if not self.current_file:
            return
        folder = os.path.dirname(self.current_file)
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}
        files = sorted([f for f in os.listdir(folder)
                        if os.path.splitext(f)[1].lower() in exts])
        if files:
            try:
                idx = files.index(os.path.basename(self.current_file))
                self.nav_label.configure(text=f"{idx + 1} / {len(files)}")
            except ValueError:
                pass

    # ──────────────────────────────────────────
    #  Affichage
    # ──────────────────────────────────────────
    def _display_image(self):
        if not self.current_image:
            return
        self.image_frame.update_idletasks()
        max_w = max(self.image_frame.winfo_width() - 10, 100)
        max_h = max(self.image_frame.winfo_height() - 10, 100)

        w = int(self.current_image.width * self.zoom_factor)
        h = int(self.current_image.height * self.zoom_factor)
        w = max(1, w)
        h = max(1, h)

        resized = self.current_image.resize((w, h), Image.LANCZOS)
        # Convertir en RGB pour CTkImage
        if resized.mode == "RGBA":
            bg = Image.new("RGB", resized.size, (30, 30, 46))
            bg.paste(resized, mask=resized.split()[3])
            resized = bg
        else:
            resized = resized.convert("RGB")

        self.photo_image = ImageTk.PhotoImage(resized)
        self.image_label.configure(image=self.photo_image, text="")
        self.image_label.image = self.photo_image
        self.zoom_label.configure(text=f"{int(self.zoom_factor * 100)}%")

    # ──────────────────────────────────────────
    #  Zoom
    # ──────────────────────────────────────────
    def zoom_in(self, factor=1.15):
        self.zoom_factor = min(self.zoom_factor * factor, 10.0)
        self._display_image()

    def zoom_out(self, factor=1.15):
        self.zoom_factor = max(self.zoom_factor / factor, 0.05)
        self._display_image()

    def zoom_fit(self):
        self.zoom_factor = 1.0
        self._display_image()

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in(1.1)
        else:
            self.zoom_out(1.1)

    # ──────────────────────────────────────────
    #  Rotation / flip
    # ──────────────────────────────────────────
    def rotate(self, angle: int):
        if not self.current_image:
            return
        self._push_history()
        self.current_image = self.current_image.rotate(-angle, expand=True)
        self._display_image()

    def flip_horizontal(self):
        if not self.current_image:
            return
        self._push_history()
        self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
        self._display_image()

    def flip_vertical(self):
        if not self.current_image:
            return
        self._push_history()
        self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
        self._display_image()

    # ──────────────────────────────────────────
    #  Filtres
    # ──────────────────────────────────────────
    def apply_filter(self, choice: str):
        if not self.original_image:
            return
        self._push_history()
        img = self.original_image.copy().convert("RGBA")

        if choice == "N&B":
            img = img.convert("L").convert("RGBA")
        elif choice == "Sépia":
            gray = img.convert("L")
            sepia = Image.merge("RGB", [
                gray.point(lambda p: min(255, int(p * 1.08))),
                gray.point(lambda p: min(255, int(p * 0.85))),
                gray.point(lambda p: min(255, int(p * 0.66))),
            ])
            img = sepia.convert("RGBA")
        elif choice == "Flou":
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
        elif choice == "Netteté":
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
        elif choice == "Contours":
            rgb = img.convert("RGB").filter(ImageFilter.FIND_EDGES)
            img = rgb.convert("RGBA")

        self.current_image = img
        self._display_image()

    # ──────────────────────────────────────────
    #  Réglages luminosité / contraste / saturation
    # ──────────────────────────────────────────
    def _apply_adjustments(self, _=None):
        if not self.original_image:
            return
        img = self.original_image.copy().convert("RGB")
        img = ImageEnhance.Brightness(img).enhance(self.brightness_slider.get())
        img = ImageEnhance.Contrast(img).enhance(self.contrast_slider.get())
        img = ImageEnhance.Color(img).enhance(self.saturation_slider.get())
        self.current_image = img.convert("RGBA")
        self._display_image()

    # ──────────────────────────────────────────
    #  Undo / reset
    # ──────────────────────────────────────────
    def _push_history(self):
        if self.current_image:
            self._history.append(self.current_image.copy())
            if len(self._history) > 20:
                self._history.pop(0)

    def undo(self):
        if self._history:
            self.current_image = self._history.pop()
            self._display_image()

    def reset_image(self):
        if self.original_image:
            self._push_history()
            self.current_image = self.original_image.copy()
            self.zoom_factor = 1.0
            self.brightness_slider.set(1.0)
            self.contrast_slider.set(1.0)
            self.saturation_slider.set(1.0)
            self.filter_menu.set("Aucun")
            self._display_image()

    # ──────────────────────────────────────────
    #  Sauvegarde
    # ──────────────────────────────────────────
    def save_image(self):
        if not self.current_image:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if path:
            try:
                save_img = self.current_image.convert("RGB") if path.endswith(".jpg") else self.current_image
                save_img.save(path)
                self.file_label.configure(text=f"💾 Sauvegardé : {os.path.basename(path)}")
            except Exception as e:
                self.file_label.configure(text=f"⚠ Erreur sauvegarde : {e}")

    # ──────────────────────────────────────────
    #  Plein écran / thème
    # ──────────────────────────────────────────
    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.winfo_toplevel().attributes("-fullscreen", self._fullscreen)
        if self._fullscreen:
            self.winfo_toplevel().bind("<Escape>", lambda e: self.toggle_fullscreen())

    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if mode == "Dark" else "Dark")

    # ──────────────────────────────────────────
    #  Utilitaires
    # ──────────────────────────────────────────
    @staticmethod
    def _file_size(path: str) -> str:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} o"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} Ko"
        else:
            return f"{size / 1024 ** 2:.1f} Mo"


# ─────────────────────────────────────────────
#  Lancement
# ─────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Photo Viewer Pro")
    root.geometry("1100x720")
    root.minsize(800, 560)

    viewer = PhotoViewer(root)
    viewer.pack(fill="both", expand=True)

    root.mainloop()
