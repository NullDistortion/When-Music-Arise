import customtkinter as ctk
from .traditional_view import TraditionalView
from .modern_view import ModernView

class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("When Music Arise")
        self.geometry("900x700")

        self.vista_activa = None

        self.barra_superior = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.barra_superior.pack(fill="x", side="top")

        self.btn_alternar_vista = ctk.CTkButton(self.barra_superior, text="Cambiar Vista")
        self.btn_alternar_vista.pack(side="left", padx=10, pady=15)

        self.btn_abrir_traveller = ctk.CTkButton(self.barra_superior, text="Rutas (Traveller)", fg_color="gray40")
        self.btn_abrir_traveller.pack(side="left", padx=10, pady=15)

        self.btn_abrir_artist = ctk.CTkButton(self.barra_superior, text="Estilos (Artist)", fg_color="gray40")
        self.btn_abrir_artist.pack(side="left", padx=10, pady=15)

        self.btn_abrir_picard = ctk.CTkButton(self.barra_superior, text="Abrir Picard")
        self.btn_abrir_picard.pack(side="right", padx=10, pady=15)

        self.contenedor_central = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_central.pack(fill="both", expand=True, padx=20, pady=20)

    def inyectar_estilos(self, modo_apariencia: str, color_acento: str):
        ctk.set_appearance_mode(modo_apariencia)
        ctk.set_default_color_theme(color_acento)

    def renderizar_vista(self, tipo_vista: str) -> ctk.CTkFrame:
        if self.vista_activa:
            self.vista_activa.destroy()

        if tipo_vista == "tradicional":
            self.vista_activa = TraditionalView(self.contenedor_central)
        else:
            self.vista_activa = ModernView(self.contenedor_central)
            
        self.vista_activa.pack(fill="both", expand=True)
        return self.vista_activa

    # Vinculaciones para el main_controller
    def vincular_alternar_vista(self, callback):
        self.btn_alternar_vista.configure(command=callback)

    def vincular_abrir_traveller(self, callback):
        self.btn_abrir_traveller.configure(command=callback)

    def vincular_abrir_artist(self, callback):
        self.btn_abrir_artist.configure(command=callback)

    def vincular_abrir_picard(self, callback):
        self.btn_abrir_picard.configure(command=callback)