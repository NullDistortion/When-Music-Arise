import os
import glob
import sys
import tkinter as tk
import customtkinter as ctk
from src.utils.path_helper import obtener_ruta_absoluta

class ControladorDescarga:
    def __init__(self, servicio_descarga, modelo_viajero):
        self.servicio_descarga = servicio_descarga
        self.modelo_viajero = modelo_viajero
        
        self.controlador_picad = None
        self.vista_activa = None
        self.callback_topbar = None
        self.gestor_cancelacion = None
        
        self.descargando = False
        self.progreso_actual = 0.0
        self.estado_texto = "Esperando..."
        self.logs_acumulados = []
        self.datos_memoria = {}

    def establecer_controlador_picard(self, controlador): self.controlador_picad = controlador
    def establecer_callback_topbar(self, callback): self.callback_topbar = callback
    def establecer_gestor_cancelacion(self, gestor): self.gestor_cancelacion = gestor

    def guardar_estado_actual(self):
        if self.vista_activa:
            try: self.datos_memoria = self.vista_activa.obtener_datos_descarga()
            except Exception: pass

    def establecer_vista_activa(self, vista):
        self.vista_activa = vista
        self.vista_activa.vincular_descarga(self.procesar_descarga)
        
        if self.gestor_cancelacion:
            self.vista_activa.vincular_cancelacion(self.gestor_cancelacion.solicitar_cancelacion)

        if self.datos_memoria:
            self.vista_activa.restaurar_datos(self.datos_memoria)

        estado_ui = "disabled" if self.descargando else "normal"
        self.vista_activa.alternar_estado_controles(estado_ui)

        if hasattr(self.vista_activa, "actualizar_progreso"):
            self.vista_activa.actualizar_progreso(self.progreso_actual, self.estado_texto)
        elif hasattr(self.vista_activa, "agregar_log"):
            self.vista_activa.caja_logs.configure(state="normal")
            self.vista_activa.caja_logs.delete("1.0", "end")
            self.vista_activa.caja_logs.insert("end", "".join(self.logs_acumulados))
            self.vista_activa.caja_logs.see("end")
            self.vista_activa.caja_logs.configure(state="disabled")

    def procesar_descarga(self):
        datos = self.vista_activa.obtener_datos_descarga()
        enlace_musica = datos.get("enlace", "").strip()
        calidad_audio = datos.get("calidad", "")

        if not enlace_musica:
            self.despachar_mensaje_vista("Error: El enlace no puede estar vacío.")
            return

        rutas = self.modelo_viajero.leer_rutas()
        ruta_descarga = rutas.get("ruta_descarga", "")

        if not ruta_descarga:
            self.despachar_mensaje_vista("Error: Configura el directorio en Traveller primero.")
            return

        self.descargando = True
        self.progreso_actual = 0.0
        self.logs_acumulados = []
        
        self.vista_activa.alternar_estado_controles("disabled")
        if self.callback_topbar: self.callback_topbar("disabled")
            
        self.despachar_mensaje_vista("Iniciando motor de descarga...")

        self.servicio_descarga.ejecutar_descarga(
            enlace=enlace_musica,
            calidad=calidad_audio,
            ruta_destino=ruta_descarga,
            callback_progreso=self.actualizar_progreso_vista,
            callback_texto=self.despachar_mensaje_vista,
            callback_fin=self._retorno_hilo_seguro
        )

    def despachar_mensaje_vista(self, mensaje: str):
        self.estado_texto = mensaje
        self.logs_acumulados.append(mensaje + "\n")
        if hasattr(self.vista_activa, "agregar_log"): self.vista_activa.agregar_log(mensaje)
        elif hasattr(self.vista_activa, "lbl_estado"): self.vista_activa.lbl_estado.configure(text=mensaje)

    def actualizar_progreso_vista(self, porcentaje: float):
        self.progreso_actual = porcentaje
        if hasattr(self.vista_activa, "actualizar_progreso"):
            self.vista_activa.actualizar_progreso(porcentaje, self.estado_texto)

    def _retorno_hilo_seguro(self, exito: bool, errores_detectados: list):
        if self.vista_activa:
            self.vista_activa.after(0, lambda: self.finalizar_descarga(exito, errores_detectados))

    def finalizar_descarga(self, exito: bool, errores_detectados: list):
        self.descargando = False
        self.vista_activa.alternar_estado_controles("normal")
        if self.callback_topbar: self.callback_topbar("normal")
        
        if errores_detectados:
            self._mostrar_popup_errores(errores_detectados)
        
        if exito and self.controlador_picad:
            datos = self.vista_activa.obtener_datos_descarga()
            if datos.get("auto_picard", False):
                rutas = self.modelo_viajero.leer_rutas()
                ruta_descarga = rutas.get("ruta_descarga", "")
                
                if os.path.exists(ruta_descarga):
                    archivos_mp3 = glob.glob(os.path.join(ruta_descarga, "*.mp3"))
                    if archivos_mp3:
                        self.despachar_mensaje_vista("Lanzando Picard automáticamente...")
                        self.controlador_picad.abrir_picard()
                    else:
                        self.despachar_mensaje_vista("⚠ Picard omitido: No se encontraron archivos .mp3 en la carpeta destino.")
                else:
                    self.despachar_mensaje_vista("⚠ Error: La carpeta de descarga no existe.")

    def _mostrar_popup_errores(self, errores: list):
        ventana_error = ctk.CTkToplevel(self.vista_activa)
        ventana_error.title("Reporte de Elementos Omitidos")
        ventana_error.geometry("550x350")
        ventana_error.grab_set() 
        
        # INYECCIÓN MULTIPLATAFORMA DEL ÍCONO
        if sys.platform == "win32":
            ruta_icono = obtener_ruta_absoluta(os.path.join("assets", "imgs", "logo.ico"))
            if os.path.exists(ruta_icono):
                ventana_error.after(200, lambda: ventana_error.iconbitmap(ruta_icono))
        else:
            ruta_icono = obtener_ruta_absoluta(os.path.join("assets", "imgs", "logo.png"))
            if os.path.exists(ruta_icono):
                try:
                    img = tk.PhotoImage(file=ruta_icono)
                    ventana_error.after(200, lambda: ventana_error.iconphoto(False, img))
                except Exception:
                    pass
        
        lbl_titulo = ctk.CTkLabel(ventana_error, text="⚠ Se omitieron algunos elementos:", font=("Arial", 16, "bold"), text_color="#d68910")
        lbl_titulo.pack(pady=(15, 5))
        
        caja_texto = ctk.CTkTextbox(ventana_error, width=500, height=200, font=("Arial", 12))
        caja_texto.pack(pady=10)
        
        texto_final = ""
        for i, error_txt in enumerate(errores, start=1):
            texto_final += f"{i}) {error_txt}\n\n"
            
        caja_texto.insert("0.0", texto_final)
        caja_texto.configure(state="disabled") 
        
        btn_aceptar = ctk.CTkButton(ventana_error, text="Entendido", command=ventana_error.destroy)
        btn_aceptar.pack(pady=10)