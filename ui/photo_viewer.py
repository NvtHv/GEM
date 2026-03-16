import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk


class PhotoViewer(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.current_file = None
        self.current_image = None
        self.photo_image = None

        self.label = ctk.CTkLabel(self, text="Photo Viewer", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)

        self.open_btn = ctk.CTkButton(self, text="Choisir une image", command=self.open_image)
        self.open_btn.pack(pady=8)

        self.file_label = ctk.CTkLabel(self, text="Aucune image sélectionnée.")
        self.file_label.pack(pady=8)

        self.image_frame = ctk.CTkFrame(self, width=800, height=420, fg_color="#1f1f2a")
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.image_frame.pack_propagate(False)

        self.image_label = ctk.CTkLabel(self.image_frame, text="")
        self.image_label.pack(fill="both", expand=True)

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Sélectionner une photo",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PNG", "*.png"),
                ("JPG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("GIF", "*.gif"),
                ("TIFF", "*.tiff"),
            ],
        )
        if path:
            self.current_file = path
            self.file_label.configure(text=f"Image sélectionnée : {path}")
            self.load_image()
        else:
            self.current_file = None
            self.current_image = None
            self.photo_image = None
            self.file_label.configure(text="Aucune image sélectionnée.")
            self.image_label.configure(image="", text="")

    def load_image(self):
        try:
            img = Image.open(self.current_file)
            self.current_image = img
            self._display_image()
        except Exception as exc:
            self.file_label.configure(text=f"Erreur chargement image : {exc}")
            self.current_image = None
            self.photo_image = None
            self.image_label.configure(image="", text="")

    def _display_image(self):
        if not self.current_image:
            return

        max_width = 900
        max_height = 500

        width, height = self.current_image.size
        ratio = min(max_width / width, max_height / height, 1)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        resized = self.current_image.resize((new_width, new_height), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(resized)

        self.image_label.configure(image=self.photo_image, text="")
        self.image_label.image = self.photo_image