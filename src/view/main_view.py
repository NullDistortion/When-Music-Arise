import customtkinter as ctk
import os
from .traditional_view import TraditionalView
from .modern_view import ModernView
from src.utils.theme_provider import PROVEEDOR_TEMAS

class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("When Music Arise")
        ancho_ventana = 850
        alto_ventana = 520
        pos_x = int((self.winfo_screenwidth() / 2) - (ancho_ventana / 2))
        pos_y = int((self.winfo_screenheight() / 2) - (alto_ventana / 2))
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")

        ruta_icono = os.path.join("assets", "imgs", "logo.ico")
        if os.path.exists(ruta_icono):
            self.iconbitmap(ruta_icono)

        self.vista_activa = None
        self.tema_actual = PROVEEDOR_TEMAS["Windows Classic"] 

        self.barra_superior = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.barra_superior.pack(fill="x", side="top")

        self.btn_alternar_vista = ctk.CTkButton(self.barra_superior, text="Cambiar Vista")
        self.btn_alternar_vista.pack(side="left", padx=10, pady=15)

        self.btn_abrir_traveller = ctk.CTkButton(self.barra_superior, text="Rutas")
        self.btn_abrir_traveller.pack(side="left", padx=10, pady=15)

        self.btn_abrir_artist = ctk.CTkButton(self.barra_superior, text="Estilos")
        self.btn_abrir_artist.pack(side="left", padx=10, pady=15)

        self.btn_abrir_picard = ctk.CTkButton(self.barra_superior, text="Abrir Picard")
        self.btn_abrir_picard.pack(side="right", padx=10, pady=15)

        self.contenedor_central = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_central.pack(fill="both", expand=True, padx=20, pady=20)

    def inyectar_estilos(self, nombre_tema: str):
        ctk.set_appearance_mode("Dark") 
        self.tema_actual = PROVEEDOR_TEMAS.get(nombre_tema, PROVEEDOR_TEMAS["Windows Classic"])
        self.configure(fg_color=self.tema_actual["fg_color"])
        self._aplicar_color_recursivo(self, self.tema_actual)

    def _aplicar_color_recursivo(self, widget, tema):
        try:
            if isinstance(widget, ctk.CTkButton):
                widget.configure(
                    fg_color=tema["button_color"], 
                    text_color=tema["text_color"], 
                    hover_color=tema["button_hover"],
                    corner_radius=tema["corner_radius"],
                    border_width=tema["border_width"],
                    border_color=tema["accent"],
                    font=tema["font"]
                )
            elif isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color="transparent")
            elif isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=tema["text_color"], font=tema["font"])
            elif isinstance(widget, ctk.CTkEntry) or isinstance(widget, ctk.CTkTextbox):
                widget.configure(
                    fg_color=tema["text_bg"], 
                    text_color=tema["text_color"], 
                    border_color=tema["accent"],
                    font=tema["font"],
                    corner_radius=tema["corner_radius"]
                )
            elif isinstance(widget, ctk.CTkComboBox):
                widget.configure(
                    fg_color=tema["text_bg"], 
                    text_color=tema["text_color"], 
                    button_color=tema["button_color"], 
                    button_hover_color=tema["button_hover"],
                    border_color=tema["accent"],
                    font=tema["font"],
                    corner_radius=tema["corner_radius"]
                )
            elif isinstance(widget, ctk.CTkProgressBar):
                widget.configure(progress_color=tema["accent"])
        except Exception:
            pass

        for hijo in widget.winfo_children():
            self._aplicar_color_recursivo(hijo, tema)

    def renderizar_vista(self, tipo_vista: str) -> ctk.CTkFrame:
        if self.vista_activa:
            self.vista_activa.destroy()

        if tipo_vista == "tradicional":
            self.vista_activa = TraditionalView(self.contenedor_central)
        else:
            self.vista_activa = ModernView(self.contenedor_central)
            
        self.vista_activa.pack(fill="both", expand=True)
        self._aplicar_color_recursivo(self.vista_activa, self.tema_actual)
        return self.vista_activa

    def vincular_alternar_vista(self, callback): 
        self.btn_alternar_vista.configure(command=callback)
    def vincular_abrir_traveller(self, callback): 
        self.btn_abrir_traveller.configure(command=callback)
    def vincular_abrir_artist(self, callback): 
        self.btn_abrir_artist.configure(command=callback)
    def vincular_abrir_picard(self, callback): 
        self.btn_abrir_picard.configure(command=callback)