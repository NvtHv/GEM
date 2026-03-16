import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import os
import platform
import subprocess
import fitz


class PDFViewer(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.doc = None
        self.zoom_level = 1.0

        # Titre
        self.label = ctk.CTkLabel(self, text="📄 Lecteur PDF", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=10)

        # Frame principal divisé en deux parties
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Frame pour les contrôles (gauche)
        self.control_panel = ctk.CTkFrame(self.main_frame, width=200)
        self.control_panel.pack(side="left", fill="y", padx=(0, 10))
        self.control_panel.pack_propagate(False)

        # Frame pour l'affichage PDF (droite)
        self.display_frame = ctk.CTkFrame(self.main_frame)
        self.display_frame.pack(side="right", fill="both", expand=True)

        # ===== PANEL DE CONTRÔLE =====
        # Bouton ouvrir
        self.open_btn = ctk.CTkButton(
            self.control_panel, 
            text="📂 Ouvrir un PDF", 
            command=self.open_pdf,
            height=40
        )
        self.open_btn.pack(pady=10, padx=10, fill="x")

        # Informations fichier
        self.file_frame = ctk.CTkFrame(self.control_panel)
        self.file_frame.pack(pady=5, padx=10, fill="x")

        self.file_label = ctk.CTkLabel(
            self.file_frame, 
            text="Aucun fichier", 
            wraplength=180,
            font=ctk.CTkFont(size=11)
        )
        self.file_label.pack(pady=5)

        # Navigation pages
        self.page_frame = ctk.CTkFrame(self.control_panel)
        self.page_frame.pack(pady=10, padx=10, fill="x")

        self.page_label = ctk.CTkLabel(self.page_frame, text="Page: 0/0")
        self.page_label.pack(pady=5)

        self.page_nav_frame = ctk.CTkFrame(self.page_frame)
        self.page_nav_frame.pack(pady=5)

        self.prev_btn = ctk.CTkButton(
            self.page_nav_frame, 
            text="◀", 
            width=40,
            command=self.prev_page,
            state="disabled"
        )
        self.prev_btn.pack(side="left", padx=2)

        self.page_entry = ctk.CTkEntry(self.page_nav_frame, width=50, justify="center")
        self.page_entry.pack(side="left", padx=2)
        self.page_entry.bind("<Return>", self.go_to_page)

        self.next_btn = ctk.CTkButton(
            self.page_nav_frame, 
            text="▶", 
            width=40,
            command=self.next_page,
            state="disabled"
        )
        self.next_btn.pack(side="left", padx=2)

        # Contrôle zoom
        self.zoom_frame = ctk.CTkFrame(self.control_panel)
        self.zoom_frame.pack(pady=10, padx=10, fill="x")

        self.zoom_label = ctk.CTkLabel(self.zoom_frame, text="Zoom: 100%")
        self.zoom_label.pack(pady=5)

        self.zoom_slider = ctk.CTkSlider(
            self.zoom_frame, 
            from_=0.5, 
            to=2.0, 
            command=self.zoom_change
        )
        self.zoom_slider.pack(pady=5, fill="x")
        self.zoom_slider.set(1.0)

        # Bouton ouvrir externe
        self.open_ext_btn = ctk.CTkButton(
            self.control_panel, 
            text="📎 Ouvrir dans application par défaut", 
            command=self.open_in_default,
            state="disabled",
            fg_color="gray"
        )
        self.open_ext_btn.pack(pady=10, padx=10, fill="x")

        # ===== ZONE D'AFFICHAGE PDF =====
        # Canvas avec scrollbar pour le PDF
        self.canvas_frame = ctk.CTkFrame(self.display_frame)
        self.canvas_frame.pack(fill="both", expand=True)

        # Créer un canvas Tkinter standard (CustomTkinter n'a pas de canvas)
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg='white',
            highlightthickness=0
        )
        
        # Scrollbars
        self.v_scrollbar = ctk.CTkScrollbar(
            self.canvas_frame, 
            orientation="vertical",
            command=self.canvas.yview
        )
        self.h_scrollbar = ctk.CTkScrollbar(
            self.canvas_frame, 
            orientation="horizontal",
            command=self.canvas.xview
        )
        
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        # Placement
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Image ID pour le canvas
        self.image_on_canvas = None

        # Status bar
        self.status_label = ctk.CTkLabel(
            self, 
            text="Prêt", 
            anchor="w",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=2)

    def open_pdf(self):
        """Ouvre un fichier PDF."""
        path = filedialog.askopenfilename(
            title="Sélectionner un fichier PDF", 
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
        )
        
        if path:
            try:
                # Fermer l'ancien document
                if self.doc:
                    self.doc.close()
                
                # Ouvrir le nouveau document avec PyMuPDF
                self.doc = fitz.open(path)
                self.current_file = path
                self.total_pages = len(self.doc)
                self.current_page = 0
                
                # Mettre à jour l'interface
                filename = os.path.basename(path)
                self.file_label.configure(text=f"📄 {filename}")
                self.label.configure(text=f"📄 {filename[:20]}{'...' if len(filename) > 20 else ''}")
                
                # Activer les contrôles
                self.open_ext_btn.configure(state="normal")
                self.prev_btn.configure(state="normal")
                self.next_btn.configure(state="normal")
                
                # Afficher la première page
                self.show_page(0)
                
                self.status_label.configure(text=f"✅ PDF chargé: {filename}")
                
            except Exception as e:
                self.status_label.configure(text=f"❌ Erreur: {str(e)}")
                self.doc = None
        else:
            self.current_file = None
            self.file_label.configure(text="Aucun fichier")
            self.open_ext_btn.configure(state="disabled")
            self.status_label.configure(text="Aucun fichier sélectionné")

    def show_page(self, page_num):
        """Affiche une page spécifique."""
        if not self.doc or page_num < 0 or page_num >= self.total_pages:
            return

        try:
            # Obtenir la page
            page = self.doc[page_num]
            
            # Appliquer le zoom
            zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Convertir en image Tkinter
            from PIL import Image, ImageTk
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.photo = ImageTk.PhotoImage(img)
            
            # Mettre à jour le canvas
            if self.image_on_canvas:
                self.canvas.delete(self.image_on_canvas)
            
            self.canvas.configure(scrollregion=(0, 0, pix.width, pix.height))
            self.image_on_canvas = self.canvas.create_image(
                0, 0, 
                anchor="nw", 
                image=self.photo
            )
            
            # Mettre à jour les labels
            self.current_page = page_num
            self.page_label.configure(text=f"Page: {page_num + 1}/{self.total_pages}")
            self.page_entry.delete(0, "end")
            self.page_entry.insert(0, str(page_num + 1))
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Erreur affichage: {str(e)}")

    def prev_page(self):
        """Page précédente."""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def next_page(self):
        """Page suivante."""
        if self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)

    def go_to_page(self, event=None):
        """Va à une page spécifique."""
        try:
            page = int(self.page_entry.get()) - 1
            if 0 <= page < self.total_pages:
                self.show_page(page)
        except ValueError:
            pass

    def zoom_change(self, value):
        """Change le niveau de zoom."""
        self.zoom_level = value
        self.zoom_label.configure(text=f"Zoom: {int(value * 100)}%")
        if self.doc:
            self.show_page(self.current_page)

    def zoom_in(self):
        if self.zoom_level < 2.0:
            self.zoom_level = min(2.0, self.zoom_level + 0.1)
            self.zoom_slider.set(self.zoom_level)
            self.show_page(self.current_page)

    def zoom_out(self):
        if self.zoom_level > 0.5:
            self.zoom_level = max(0.5, self.zoom_level - 0.1)
            self.zoom_slider.set(self.zoom_level)
            self.show_page(self.current_page)

    def scroll_down(self):
        self.canvas.yview_scroll(1, 'units')

    def scroll_up(self):
        self.canvas.yview_scroll(-1, 'units')

    def open_in_default(self):
        """Ouvre le PDF dans l'application par défaut."""
        if not self.current_file:
            return

        try:
            if platform.system() == "Windows":
                os.startfile(self.current_file)
            elif platform.system() == "Darwin":
                subprocess.call(["open", self.current_file])
            else:
                subprocess.call(["xdg-open", self.current_file])
            
            self.status_label.configure(text="📎 Ouvert dans application externe")
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Erreur: {str(e)}")

    def destroy(self):
        """Nettoie les ressources."""
        if self.doc:
            self.doc.close()
        super().destroy()