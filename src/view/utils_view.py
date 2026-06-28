import customtkinter as ctk
from customtkinter import filedialog

class UtilsView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configuración de Rutas (Traveller)")
        self.geometry("600x350")
        self.grab_set() 

        # --- Fila Descarga ---
        self.lbl_descarga = ctk.CTkLabel(self, text="Directorio de Descarga:", font=("Arial", 12, "bold"))
        self.lbl_descarga.pack(anchor="w", padx=20, pady=(20, 5))
        
        fila_descarga = ctk.CTkFrame(self, fg_color="transparent")
        fila_descarga.pack(fill="x", padx=20, pady=5)
        
        self.entrada_descarga = ctk.CTkEntry(fila_descarga, width=420)
        self.entrada_descarga.pack(side="left", padx=(0, 10))
        
        self.btn_exp_descarga = ctk.CTkButton(fila_descarga, text="Explorar...", width=100, command=self._seleccionar_carpeta)
        self.btn_exp_descarga.pack(side="left")

        # --- Fila Picard ---
        self.lbl_picard = ctk.CTkLabel(self, text="Ruta del ejecutable de Picard (.exe):", font=("Arial", 12, "bold"))
        self.lbl_picard.pack(anchor="w", padx=20, pady=(20, 5))

        fila_picard = ctk.CTkFrame(self, fg_color="transparent")
        fila_picard.pack(fill="x", padx=20, pady=5)

        self.entrada_picard = ctk.CTkEntry(fila_picard, width=420)
        self.entrada_picard.pack(side="left", padx=(0, 10))

        self.btn_exp_picard = ctk.CTkButton(fila_picard, text="Explorar...", width=100, command=self._seleccionar_archivo)
        self.btn_exp_picard.pack(side="left")

        # --- Guardar ---
        self.btn_guardar = ctk.CTkButton(self, text="Guardar Rutas", fg_color="green")
        self.btn_guardar.pack(pady=30)

    def _seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de descargas")
        if carpeta:
            self.entrada_descarga.delete(0, "end")
            self.entrada_descarga.insert(0, carpeta)

    def _seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(title="Seleccionar ejecutable de Picard", filetypes=[("Ejecutables", "*.exe"), ("Todos los archivos", "*.*")])
        if archivo:
            self.entrada_picard.delete(0, "end")
            self.entrada_picard.insert(0, archivo)

    def vincular_guardado(self, callback): self.btn_guardar.configure(command=callback)
        
    def obtener_rutas(self) -> dict:
        return {"ruta_descarga": self.entrada_descarga.get(), "ruta_picard": self.entrada_picard.get()}

    def cargar_rutas(self, ruta_descarga: str, ruta_picard: str):
        self.entrada_descarga.delete(0, "end")
        self.entrada_descarga.insert(0, ruta_descarga)
        self.entrada_picard.delete(0, "end")
        self.entrada_picard.insert(0, ruta_picard)