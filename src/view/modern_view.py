import customtkinter as ctk
from .mother_view import MotherView

class ModernView(MotherView):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.barra_progreso = ctk.CTkProgressBar(self, width=500)
        self.barra_progreso.set(0)
        self.barra_progreso.pack(pady=(40, 10))

        self.lbl_estado = ctk.CTkLabel(self, text="Esperando...", font=("Arial", 12))
        self.lbl_estado.pack(pady=5)

    def actualizar_progreso(self, porcentaje: float, mensaje: str = "Descargando..."):
        self.barra_progreso.set(porcentaje / 100.0)
        self.lbl_estado.configure(text=f"{mensaje} ({porcentaje}%)")