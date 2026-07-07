import customtkinter as ctk
from customtkinter import filedialog
import sys
import os
import tkinter as tk
from src.utils.path_helper import obtener_ruta_absoluta

class UtilsView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configuración de Rutas (Traveller)")
        self.geometry("600x320")
        self.grab_set() 

        if sys.platform == "win32":
            ruta_icono = obtener_ruta_absoluta(os.path.join("assets", "imgs", "logo.ico"))
            if os.path.exists(ruta_icono):
                self.after(200, lambda: self.iconbitmap(ruta_icono))
        else:
            ruta_icono = obtener_ruta_absoluta(os.path.join("assets", "imgs", "logo.png"))
            if os.path.exists(ruta_icono):
                try:
                    img = tk.PhotoImage(file=ruta_icono)
                    self.after(200, lambda: self.iconphoto(False, img))
                except Exception:
                    pass
            
        self.lbl_descarga = ctk.CTkLabel(self, text="Directorio de Descarga:", font=("Arial", 12, "bold"))
        self.lbl_descarga.pack(anchor="w", padx=20, pady=(15, 5))
        
        fila_descarga = ctk.CTkFrame(self, fg_color="transparent")
        fila_descarga.pack(fill="x", padx=20, pady=5)
        
        self.entrada_descarga = ctk.CTkEntry(fila_descarga, width=420)
        self.entrada_descarga.pack(side="left", padx=(0, 10))
        
        self.btn_exp_descarga = ctk.CTkButton(fila_descarga, text="Explorar...", width=100, command=self._seleccionar_carpeta)
        self.btn_exp_descarga.pack(side="left")

        self.lbl_picard = ctk.CTkLabel(self, text="Ruta del ejecutable de Picard (Opcional):", font=("Arial", 12, "bold"))
        self.lbl_picard.pack(anchor="w", padx=20, pady=(10, 5))

        fila_picard = ctk.CTkFrame(self, fg_color="transparent")
        fila_picard.pack(fill="x", padx=20, pady=5)

        self.entrada_picard = ctk.CTkEntry(fila_picard, width=420)
        self.entrada_picard.pack(side="left", padx=(0, 10))

        self.btn_exp_picard = ctk.CTkButton(fila_picard, text="Explorar...", width=100, command=self._seleccionar_archivo_picard)
        self.btn_exp_picard.pack(side="left")

        # NUEVO COMPONENTE: Archivo de Cookies
        self.lbl_cookies = ctk.CTkLabel(self, text="Archivo de Cookies .txt (Opcional - Restricción de edad):", font=("Arial", 12, "bold"))
        self.lbl_cookies.pack(anchor="w", padx=20, pady=(10, 5))

        fila_cookies = ctk.CTkFrame(self, fg_color="transparent")
        fila_cookies.pack(fill="x", padx=20, pady=5)

        self.entrada_cookies = ctk.CTkEntry(fila_cookies, width=420)
        self.entrada_cookies.pack(side="left", padx=(0, 10))

        self.btn_exp_cookies = ctk.CTkButton(fila_cookies, text="Explorar...", width=100, command=self._seleccionar_archivo_cookies)
        self.btn_exp_cookies.pack(side="left")

        self.btn_guardar = ctk.CTkButton(self, text="Guardar Rutas", fg_color="green")
        self.btn_guardar.pack(pady=20)

    def _seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta")
        if carpeta:
            self.entrada_descarga.delete(0, "end")
            self.entrada_descarga.insert(0, carpeta)

    def _seleccionar_archivo_picard(self):
        filtros = [("Ejecutables", "*.exe"), ("Todos", "*.*")] if sys.platform == "win32" else [("Todos los archivos", "*.*")]
        archivo = filedialog.askopenfilename(title="Seleccionar Picard", filetypes=filtros)
        if archivo:
            self.entrada_picard.delete(0, "end")
            self.entrada_picard.insert(0, archivo)

    def _seleccionar_archivo_cookies(self):
        filtros = [("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        archivo = filedialog.askopenfilename(title="Seleccionar archivo cookies.txt", filetypes=filtros)
        if archivo:
            self.entrada_cookies.delete(0, "end")
            self.entrada_cookies.insert(0, archivo)

    def vincular_guardado(self, callback): 
        self.btn_guardar.configure(command=callback)
        
    def obtener_rutas(self) -> dict:
        return {
            "ruta_descarga": self.entrada_descarga.get(), 
            "ruta_picard": self.entrada_picard.get(),
            "ruta_cookies": self.entrada_cookies.get()
        }

    def cargar_rutas(self, ruta_descarga: str, ruta_picard: str, ruta_cookies: str):
        self.entrada_descarga.delete(0, "end")
        self.entrada_descarga.insert(0, ruta_descarga)
        
        self.entrada_picard.delete(0, "end")
        self.entrada_picard.insert(0, ruta_picard)
        
        self.entrada_cookies.delete(0, "end")
        self.entrada_cookies.insert(0, ruta_cookies)