class ControladorDescarga:
    def __init__(self, servicio_descarga, modelo_viajero):
        self.servicio_descarga = servicio_descarga
        self.modelo_viajero = modelo_viajero
        
        self.controlador_picad = None
        self.vista_activa = None
        self.callback_topbar = None
        self.gestor_cancelacion = None # Se inyectará desde el main_controller
        
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
            enlace=enlace_musica, calidad=calidad_audio, ruta_destino=ruta_descarga,
            callback_progreso=self.actualizar_progreso_vista,
            callback_texto=self.despachar_mensaje_vista,
            callback_fin=self._retorno_hilo_seguro # <-- AQUÍ SE CORRIGE EL HILO
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

    def _retorno_hilo_seguro(self, exito: bool):
        """Obliga a que la finalización y Picard ocurran en el hilo principal gráfico."""
        if self.vista_activa:
            self.vista_activa.after(0, lambda: self.finalizar_descarga(exito))

    def finalizar_descarga(self, exito: bool):
        self.descargando = False
        self.vista_activa.alternar_estado_controles("normal")
        if self.callback_topbar: self.callback_topbar("normal")
        
        if exito and self.controlador_picad:
            datos = self.vista_activa.obtener_datos_descarga()
            if datos.get("auto_picard", False):
                self.despachar_mensaje_vista("Lanzando Picard automáticamente...")
                self.controlador_picad.abrir_picard()