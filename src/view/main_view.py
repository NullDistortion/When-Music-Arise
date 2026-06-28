import customtkinter as ctk
from .traditional_view import TraditionalView
from .modern_view import ModernView

COLORES_ACENTO = {
    "Azul (Defecto)": "#1F6AA5",
    "Verde": "#2FA572",
    "Azul Oscuro": "#144870",
    "Windows XP": "#003399",
    "Tecno Caotico": "#FF003C",
    "RC": "#FF8C00",
    "Kawai": "#FFB6C1",
    "Punk Primitivo": "#8B0000"
}

class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("When Music Arise")
        self.geometry("900x700")

        self.vista_activa = None
        self.color_actual = "#1F6AA5" # Por defecto

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

    def inyectar_estilos(self, modo_apariencia: str, nombre_color: str):
        ctk.set_appearance_mode(modo_apariencia)
        self.color_actual = COLORES_ACENTO.get(nombre_color, "#1F6AA5")
        self._aplicar_color_recursivo(self, self.color_actual)

    def _aplicar_color_recursivo(self, widget, color_hex):
        """Escanea todos los elementos y aplica el color de acento a botones y barras."""
        if isinstance(widget, ctk.CTkButton) and widget.cget("text") not in ["Rutas (Traveller)", "Estilos (Artist)"]:
            widget.configure(fg_color=color_hex)
        elif isinstance(widget, ctk.CTkProgressBar):
            widget.configure(progress_color=color_hex)
        
        for hijo in widget.winfo_children():
            self._aplicar_color_recursivo(hijo, color_hex)

    def renderizar_vista(self, tipo_vista: str) -> ctk.CTkFrame:
        if self.vista_activa:
            self.vista_activa.destroy()

        if tipo_vista == "tradicional":
            self.vista_activa = TraditionalView(self.contenedor_central)
        else:
            self.vista_activa = ModernView(self.contenedor_central)
            
        self.vista_activa.pack(fill="both", expand=True)
        # Reaplicar el color a la nueva vista inyectada
        self._aplicar_color_recursivo(self.vista_activa, self.color_actual)
        return self.vista_activa

    # Vinculaciones
    def vincular_alternar_vista(self, callback): self.btn_alternar_vista.configure(command=callback)
    def vincular_abrir_traveller(self, callback): self.btn_abrir_traveller.configure(command=callback)
    def vincular_abrir_artist(self, callback): self.btn_abrir_artist.configure(command=callback)
    def vincular_abrir_picard(self, callback): self.btn_abrir_picard.configure(command=callback)