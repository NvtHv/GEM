import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import os
import platform
import subprocess
import fitz  # PyMuPDF
from PIL import Image, ImageTk, ImageDraw

class PDFViewer(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # --- Variables d'état ---
        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.doc = None
        self.zoom_level = 1.0
        self.page_width = 0
        self.page_height = 0
        self.search_query = ""
        self._is_rendering = False
        self.photo = None  # Référence pour éviter le Garbage Collection

        # --- Configuration de l'interface ---
        self.setup_ui()
        
        # --- Bindings globaux ---
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.display_container.bind("<Configure>", self.on_display_resize)

    def setup_ui(self):
        """Initialise la structure de l'interface."""
        self.label = ctk.CTkLabel(self, text="📄 Lecteur PDF Premium", font=ctk.CTkFont(size=22, weight="bold"))
        self.label.pack(pady=(10, 5))

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Panneau de Contrôle (Gauche) ---
        self.control_panel = ctk.CTkFrame(self.main_frame, width=250)
        self.control_panel.pack(side="left", fill="y", padx=(0, 10))
        self.control_panel.pack_propagate(False)

        # 1. Ouverture
        self.open_btn = ctk.CTkButton(self.control_panel, text="📂 Ouvrir un PDF", command=self.open_pdf)
        self.open_btn.pack(pady=10, padx=10, fill="x")

        self.file_label = ctk.CTkLabel(self.control_panel, text="Aucun fichier", wraplength=200, font=ctk.CTkFont(size=11))
        self.file_label.pack(pady=5)

        # 2. Recherche
        self.search_frame = ctk.CTkFrame(self.control_panel)
        self.search_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(self.search_frame, text="🔍 Recherche", font=ctk.CTkFont(weight="bold")).pack(pady=2)
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Mot-clé...")
        self.search_entry.pack(pady=5, padx=10, fill="x")
        self.search_entry.bind("<Return>", self.perform_search)
        
        search_btns = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        search_btns.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(search_btns, text="Chercher", command=self.perform_search).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(search_btns, text="X", width=30, fg_color="gray", command=self.clear_search).pack(side="left", padx=2)

        # 3. Navigation
        self.nav_frame = ctk.CTkFrame(self.control_panel)
        self.nav_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(self.nav_frame, text="Navigation", font=ctk.CTkFont(weight="bold")).pack(pady=2)
        
        btn_nav_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        btn_nav_frame.pack(pady=5)
        self.prev_btn = ctk.CTkButton(btn_nav_frame, text="◀", width=40, command=self.prev_page, state="disabled")
        self.prev_btn.pack(side="left", padx=2)
        self.page_entry = ctk.CTkEntry(btn_nav_frame, width=50, justify="center")
        self.page_entry.pack(side="left", padx=2)
        self.page_entry.bind("<Return>", self.go_to_page)
        self.next_btn = ctk.CTkButton(btn_nav_frame, text="▶", width=40, command=self.next_page, state="disabled")
        self.next_btn.pack(side="left", padx=2)
        
        self.page_total_label = ctk.CTkLabel(self.nav_frame, text="Page: 0/0")
        self.page_total_label.pack()

        # 4. Zoom
        self.zoom_frame = ctk.CTkFrame(self.control_panel)
        self.zoom_frame.pack(pady=10, padx=10, fill="x")
        self.zoom_label = ctk.CTkLabel(self.zoom_frame, text="Zoom: 100%", font=ctk.CTkFont(weight="bold"))
        self.zoom_label.pack()
        
        zoom_ctrls = ctk.CTkFrame(self.zoom_frame, fg_color="transparent")
        zoom_ctrls.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(zoom_ctrls, text="-", width=30, command=self.zoom_out).pack(side="left")
        self.zoom_slider = ctk.CTkSlider(zoom_ctrls, from_=0.3, to=3.0, command=self.zoom_change)
        self.zoom_slider.set(1.0)
        self.zoom_slider.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(zoom_ctrls, text="+", width=30, command=self.zoom_in).pack(side="left")

        self.fit_window_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.zoom_frame, text="Ajuster auto.", variable=self.fit_window_var, command=self.apply_fit).pack(pady=5)

        # 5. Externe
        self.open_ext_btn = ctk.CTkButton(self.control_panel, text="📎 Application externe", command=self.open_in_default, state="disabled")
        self.open_ext_btn.pack(side="bottom", pady=20, padx=10, fill="x")

        # --- Zone d'affichage (Droite) ---
        self.display_container = ctk.CTkFrame(self.main_frame, fg_color="gray20")
        self.display_container.pack(side="right", fill="both", expand=True)

        self.v_scrollbar = ctk.CTkScrollbar(self.display_container, orientation="vertical")
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar = ctk.CTkScrollbar(self.display_container, orientation="horizontal")
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(
            self.display_container, bg='gray20', highlightthickness=0,
            xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scrollbar.configure(command=self.canvas.yview)
        self.h_scrollbar.configure(command=self.canvas.xview)

        self.status_label = ctk.CTkLabel(self, text="Prêt", anchor="w", font=ctk.CTkFont(size=11))
        self.status_label.pack(side="bottom", fill="x", padx=10)

    # --- MÉTHODES DE NAVIGATION & FICHIER ---
    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            try:
                if self.doc: self.doc.close()
                self.doc = fitz.open(path)
                self.current_file = path
                self.total_pages = len(self.doc)
                self.current_page = 0
                page = self.doc[0]
                self.page_width, self.page_height = page.rect.width, page.rect.height
                self.file_label.configure(text=os.path.basename(path))
                self.open_ext_btn.configure(state="normal")
                self.prev_btn.configure(state="normal")
                self.next_btn.configure(state="normal")
                self.show_page(0)
            except Exception as e:
                self.status_label.configure(text=f"❌ Erreur: {e}")

    def show_page(self, page_num):
        if not self.doc or self._is_rendering: return
        self._is_rendering = True
        try:
            self.current_page = page_num
            page = self.doc[page_num]

            if self.fit_window_var.get():
                self.calculate_fit_zoom()

            # Rendu PyMuPDF
            matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=matrix)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Surlignage Recherche
            if self.search_query:
                overlay = Image.new('RGBA', img.size, (255, 255, 0, 0))
                draw = ImageDraw.Draw(overlay)
                for rect in page.search_for(self.search_query):
                    scaled = [rect.x0 * self.zoom_level, rect.y0 * self.zoom_level,
                              rect.x1 * self.zoom_level, rect.y1 * self.zoom_level]
                    draw.rectangle(scaled, fill=(255, 255, 0, 100))
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            
            # Centrage si plus petit que le canvas
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            cx, cy = max(img.width, cw) / 2, max(img.height, ch) / 2
            
            self.canvas.create_image(cx, cy, image=self.photo, anchor="center")
            self.canvas.config(scrollregion=(0, 0, max(img.width, cw), max(img.height, ch)))

            # Mise à jour UI
            self.page_total_label.configure(text=f"Page: {page_num + 1}/{self.total_pages}")
            self.page_entry.delete(0, "end")
            self.page_entry.insert(0, str(page_num + 1))
            self.zoom_label.configure(text=f"Zoom: {int(self.zoom_level * 100)}%")
        finally:
            self._is_rendering = False

    # --- MÉTHODES DE ZOOM ---
    def zoom_in(self):
        if self.doc:
            self.zoom_slider.set(min(3.0, self.zoom_slider.get() + 0.2))
            self.zoom_change(self.zoom_slider.get())

    def zoom_out(self):
        if self.doc:
            self.zoom_slider.set(max(0.3, self.zoom_slider.get() - 0.2))
            self.zoom_change(self.zoom_slider.get())

    def zoom_change(self, value):
        if self.doc:
            if self.fit_window_var.get(): self.fit_window_var.set(False)
            self.zoom_level = float(value)
            self.show_page(self.current_page)

    def calculate_fit_zoom(self):
        dw = self.canvas.winfo_width() - 30
        dh = self.canvas.winfo_height() - 30
        if dw > 10 and dh > 10:
            self.zoom_level = min(dw / self.page_width, dh / self.page_height)
            self.zoom_slider.set(self.zoom_level)

    def apply_fit(self):
        if self.fit_window_var.get() and self.doc: self.show_page(self.current_page)

    # --- RECHERCHE ---
    def perform_search(self, event=None):
        query = self.search_entry.get().strip()
        if query:
            self.search_query = query
            self.show_page(self.current_page)
            self.status_label.configure(text=f"🔍 Recherche: '{query}'")
        else: self.clear_search()

    def clear_search(self):
        self.search_query = ""
        self.search_entry.delete(0, "end")
        self.show_page(self.current_page)
        self.status_label.configure(text="✅ Recherche effacée")

    # --- UTILS ---
    def _on_mousewheel(self, event):
        if not self.doc: return
        # Ctrl + Molette = Zoom
        if event.state & 0x0004:
            if event.delta > 0 or event.num == 4: self.zoom_in()
            else: self.zoom_out()
        else: # Molette simple = Scroll
            if platform.system() == "Windows":
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            else:
                if event.num == 4: self.canvas.yview_scroll(-1, "units")
                elif event.num == 5: self.canvas.yview_scroll(1, "units")

    def on_display_resize(self, event):
        if self.fit_window_var.get() and self.doc:
            if hasattr(self, '_res_id'): self.after_cancel(self._res_id)
            self._res_id = self.after(150, lambda: self.show_page(self.current_page))

    def prev_page(self):
        if self.current_page > 0: self.show_page(self.current_page - 1)

    def next_page(self):
        if self.current_page < self.total_pages - 1: self.show_page(self.current_page + 1)

    def go_to_page(self, event=None):
        try:
            val = int(self.page_entry.get()) - 1
            if 0 <= val < self.total_pages: self.show_page(val)
        except: pass

    def open_in_default(self):
        if not self.current_file: return
        try:
            if platform.system() == "Windows": os.startfile(self.current_file)
            elif platform.system() == "Darwin": subprocess.call(["open", self.current_file])
            else: subprocess.call(["xdg-open", self.current_file])
        except Exception as e: self.status_label.configure(text=f"❌ Erreur: {e}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Mon Lecteur PDF")
    app.geometry("1100x800")
    PDFViewer(app).pack(fill="both", expand=True)
    app.mainloop()