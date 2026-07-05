import customtkinter as ctk

class MotherView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.lbl_titulo = ctk.CTkLabel(self, text="When Music Arise", font=("Arial", 26, "bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        self.entrada_enlace = ctk.CTkEntry(
            self, 
            placeholder_text="Ingresa el enlace aquí...", 
            width=500,
            height=40
        )
        self.entrada_enlace.pack(pady=10)

        self.combo_calidad = ctk.CTkComboBox(
            self, 
            values=["Máxima Calidad", "Calidad Media", "Audio Rápido"],
            width=200
        )
        self.combo_calidad.pack(pady=10)

        self.var_auto_picard = ctk.BooleanVar(value=False)
        self.check_auto_picard = ctk.CTkCheckBox(
            self, 
            text="Cargar automáticamente en Picard al finalizar", 
            variable=self.var_auto_picard,
            text_color="gray50", font=("Arial", 15)
        )
        self.check_auto_picard.pack(pady=10)

        self.btn_descargar = ctk.CTkButton(self, text="Descargar", height=40)
        self.btn_descargar.pack(pady=10)

        self.lbl_aviso = ctk.CTkLabel(
            self, 
            text="💡 Consejo: Descarga la versión \"Tema\" (Álbum) en lugar del\nVideoclip Oficial para obtener un artista y título perfectos.", 
            text_color="gray50", font=("Arial", 11)
        )
        self.lbl_aviso.pack(pady=5)

    def obtener_datos_descarga(self) -> dict:
        return {
            "enlace": self.entrada_enlace.get(),
            "calidad": self.combo_calidad.get(),
            "auto_picard": self.var_auto_picard.get()
        }

    def restaurar_datos(self, datos: dict):
        self.entrada_enlace.delete(0, "end")
        self.entrada_enlace.insert(0, datos.get("enlace", ""))
        self.combo_calidad.set(datos.get("calidad", "Máxima Calidad"))
        self.var_auto_picard.set(datos.get("auto_picard", False))

    def alternar_estado_controles(self, estado: str):
        self.btn_descargar.configure(state=estado)
        self.check_auto_picard.configure(state=estado)

    def vincular_descarga(self, callback):
        self.btn_descargar.configure(command=callback)