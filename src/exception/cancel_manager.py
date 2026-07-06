import customtkinter as ctk
import os
import glob

class GestorCancelacion:
    """Maneja el flujo de pausa, confirmación y limpieza al cancelar una descarga."""
    def __init__(self, servicio_descarga, modelo_viajero, controlador_descarga):
        self.servicio_descarga = servicio_descarga
        self.modelo_viajero = modelo_viajero
        self.controlador_descarga = controlador_descarga
        self.ventana_confirmacion = None

    def solicitar_cancelacion(self):
        # 1. Pausar el flujo de lectura (Congela yt-dlp a nivel de buffer)
        self.servicio_descarga.pausar_descarga()

        # 2. Desplegar ventana emergente
        self.ventana_confirmacion = ctk.CTkToplevel()
        self.ventana_confirmacion.title("⚠ Confirmar Cancelación")
        self.ventana_confirmacion.geometry("380x150")
        self.ventana_confirmacion.grab_set() # Obliga a responder esta ventana
        self.ventana_confirmacion.protocol("WM_DELETE_WINDOW", self._reanudar) # Si cierra en la X

        lbl_pregunta = ctk.CTkLabel(
            self.ventana_confirmacion, 
            text="¿Estás seguro de que deseas cancelar la descarga?\nSe borrarán los archivos incompletos.", 
            font=("Arial", 12, "bold")
        )
        lbl_pregunta.pack(pady=(20, 15))

        frame_botones = ctk.CTkFrame(self.ventana_confirmacion, fg_color="transparent")
        frame_botones.pack()

        btn_si = ctk.CTkButton(frame_botones, text="Sí, Cancelar", fg_color="red", width=120, command=self._ejecutar_cancelacion)
        btn_si.pack(side="left", padx=10)

        btn_no = ctk.CTkButton(frame_botones, text="No, Continuar", width=120, command=self._reanudar)
        btn_no.pack(side="left", padx=10)

    def _reanudar(self):
        self.ventana_confirmacion.destroy()
        self.servicio_descarga.reanudar_descarga()

    def _ejecutar_cancelacion(self):
        self.ventana_confirmacion.destroy()
        self.controlador_descarga.despachar_mensaje_vista("Cancelando proceso y limpiando archivos...")
        
        # Matar el proceso
        self.servicio_descarga.cancelar_descarga()
        
        # Limpiar la basura
        rutas = self.modelo_viajero.leer_rutas()
        ruta_destino = rutas.get("ruta_descarga", "")
        if os.path.exists(ruta_destino):
            patrones_basura = ["*.part", "*.ytdl", "*.temp"]
            for patron in patrones_basura:
                for archivo in glob.glob(os.path.join(ruta_destino, patron)):
                    try:
                        os.remove(archivo)
                    except Exception:
                        pass
        
        self.controlador_descarga.despachar_mensaje_vista("❌ Descarga cancelada por el usuario.")