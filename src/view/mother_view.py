import customtkinter as ctk

class MotherView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.lbl_titulo = ctk.CTkLabel(self, text="When Music Arise", font=("Arial", 26, "bold"))
        self.lbl_titulo.pack(pady=(30, 20))

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

        self.btn_descargar = ctk.CTkButton(self, text="Descargar", height=40)
        self.btn_descargar.pack(pady=20)

    def obtener_datos_descarga(self) -> dict:
        return {
            "enlace": self.entrada_enlace.get(),
            "calidad": self.combo_calidad.get()
        }

    def vincular_descarga(self, callback):
        self.btn_descargar.configure(command=callback)