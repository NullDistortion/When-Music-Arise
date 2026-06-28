import customtkinter as ctk

class UtilsView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configuración de Rutas (Traveller)")
        self.geometry("550x350")
        self.grab_set() 

        self.lbl_descarga = ctk.CTkLabel(self, text="Directorio de Descarga:", font=("Arial", 12, "bold"))
        self.lbl_descarga.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.entrada_descarga = ctk.CTkEntry(self, width=500)
        self.entrada_descarga.pack(padx=20, pady=5)

        self.lbl_picard = ctk.CTkLabel(self, text="Ruta del ejecutable de Picard (.exe):", font=("Arial", 12, "bold"))
        self.lbl_picard.pack(anchor="w", padx=20, pady=(20, 5))

        self.entrada_picard = ctk.CTkEntry(self, width=500)
        self.entrada_picard.pack(padx=20, pady=5)

        self.btn_guardar = ctk.CTkButton(self, text="Guardar Rutas", fg_color="green")
        self.btn_guardar.pack(pady=30)

    def vincular_guardado(self, callback):
        self.btn_guardar.configure(command=callback)
        
    def obtener_rutas(self) -> dict:
        return {
            "ruta_descarga": self.entrada_descarga.get(),
            "ruta_picard": self.entrada_picard.get()
        }

    def cargar_rutas(self, ruta_descarga: str, ruta_picard: str):
        self.entrada_descarga.delete(0, "end")
        self.entrada_descarga.insert(0, ruta_descarga)
        self.entrada_picard.delete(0, "end")
        self.entrada_picard.insert(0, ruta_picard)