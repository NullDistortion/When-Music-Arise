import customtkinter as ctk
from .mother_view import MotherView

class TraditionalView(MotherView):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.caja_logs = ctk.CTkTextbox(self, width=600, height=250)
        self.caja_logs.pack(pady=20, padx=20, fill="both", expand=True)
        self.caja_logs.configure(state="disabled")

    def agregar_log(self, mensaje: str):
        self.caja_logs.configure(state="normal")
        self.caja_logs.insert("end", mensaje + "\n")
        self.caja_logs.see("end")
        self.caja_logs.configure(state="disabled")