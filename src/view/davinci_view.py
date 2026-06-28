import customtkinter as ctk

class DavinciView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Estilos Visuales (Artist)")
        self.geometry("400x300")
        self.grab_set()

        self.lbl_modo = ctk.CTkLabel(self, text="Modo de Apariencia:", font=("Arial", 12, "bold"))
        self.lbl_modo.pack(pady=(20, 5))
        
        self.combo_modo = ctk.CTkComboBox(self, values=["Dark", "Light", "System"])
        self.combo_modo.pack(pady=5)

        self.lbl_color = ctk.CTkLabel(self, text="Color de Acento:", font=("Arial", 12, "bold"))
        self.lbl_color.pack(pady=(20, 5))

        self.combo_color = ctk.CTkComboBox(self, values=["blue", "green", "dark-blue"])
        self.combo_color.pack(pady=5)

        self.btn_guardar = ctk.CTkButton(self, text="Aplicar y Guardar", fg_color="green")
        self.btn_guardar.pack(pady=30)

    def vincular_guardado(self, callback):
        self.btn_guardar.configure(command=callback)

    def obtener_estilos(self) -> dict:
        return {
            "modo_apariencia": self.combo_modo.get(),
            "color_acento": self.combo_color.get()
        }

    def cargar_estilos(self, modo_apariencia: str, color_acento: str):
        self.combo_modo.set(modo_apariencia)
        self.combo_color.set(color_acento)