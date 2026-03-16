import customtkinter
from ui.main_window import MainWindow


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()
