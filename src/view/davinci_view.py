import customtkinter as ctk
import os
from src.utils.theme_provider import PROVEEDOR_TEMAS

class DavinciView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Estilos Visuales (Artist)")
        self.geometry("400x200") # Tamaño reducido ya que quitamos opciones
        self.grab_set()

        # INYECCIÓN DE ÍCONO
        ruta_icono = os.path.join("assets", "imgs", "logo.ico")
        if os.path.exists(ruta_icono):
            self.after(200, lambda: self.iconbitmap(ruta_icono))

        self.lbl_color = ctk.CTkLabel(self, text="Estilo Visual (Tema):", font=("Arial", 12, "bold"))
        self.lbl_color.pack(pady=(20, 5))

        self.combo_color = ctk.CTkComboBox(self, values=list(PROVEEDOR_TEMAS.keys()))
        self.combo_color.pack(pady=5)

        self.btn_guardar = ctk.CTkButton(self, text="Aplicar y Guardar", fg_color="green")
        self.btn_guardar.pack(pady=30)

    def vincular_guardado(self, callback):
        self.btn_guardar.configure(command=callback)

    def obtener_estilos(self) -> dict:
        return {"tema": self.combo_color.get()}

    def cargar_estilos(self, tema: str):
        self.combo_color.set(tema)