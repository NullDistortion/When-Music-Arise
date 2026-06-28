class ControladorDescarga:
    def __init__(self, servicio_descarga, modelo_viajero):
        self.servicio_descarga = servicio_descarga
        self.modelo_viajero = modelo_viajero
        self.vista_activa = None

    def establecer_vista_activa(self, vista):
        """Recibe la vista instanciada (Tradicional o Moderna) y vincula su botón."""
        self.vista_activa = vista
        self.vista_activa.vincular_descarga(self.procesar_descarga)

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
            self.despachar_mensaje_vista("Error: Configura el directorio de descarga en Traveller primero.")
            return

        self.despachar_mensaje_vista("Iniciando motor de descarga...")

        # Se envía la petición al servicio. Los callbacks permiten que el servicio
        # en segundo plano actualice la interfaz sin bloquearla.
        self.servicio_descarga.ejecutar_descarga(
            enlace=enlace_musica,
            calidad=calidad_audio,
            ruta_destino=ruta_descarga,
            callback_progreso=self.actualizar_progreso_vista,
            callback_texto=self.despachar_mensaje_vista
        )

    def despachar_mensaje_vista(self, mensaje: str):
        """Actualiza la vista tradicional (logs) o moderna (estado) según corresponda."""
        if hasattr(self.vista_activa, "agregar_log"):
            self.vista_activa.agregar_log(mensaje)
        elif hasattr(self.vista_activa, "lbl_estado"):
            self.vista_activa.lbl_estado.configure(text=mensaje)

    def actualizar_progreso_vista(self, porcentaje: float):
        """Actualiza la barra de progreso solo si la vista moderna está activa."""
        if hasattr(self.vista_activa, "actualizar_progreso"):
            self.vista_activa.actualizar_progreso(porcentaje)