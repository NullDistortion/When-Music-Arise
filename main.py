import tkinter as tk
import os
import sys
import ctypes
from view import MusicDownloaderUI
from controller import MusicController

def resource_path(relative_path):
    """Obtiene ruta absoluta para PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    try:
        myappid = 'music.downloader.ultimate.v1' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
    # ---------------------------

    root = tk.Tk()
    
    # --- ICONO VENTANA ---
    try:
        icon_path = resource_path("logo.ico")
        # 'default' aplica el icono a esta ventana Y a todas las hijas
        root.iconbitmap(default=icon_path) 
    except Exception as e:
        pass

    controller = MusicController(root)
    view = MusicDownloaderUI(root, controller)
    controller.set_view(view)
    
    root.mainloop()

if __name__ == "__main__":
    main()