class ControladorConfig:
    def __init__(self, modelo_viajero):
        self.modelo_viajero = modelo_viajero
        self.vista_utils = None

    def establecer_vista(self, vista):
        self.vista_utils = vista
        
        rutas_actuales = self.modelo_viajero.leer_rutas()
        descarga = rutas_actuales.get("ruta_descarga", "")
        picard = rutas_actuales.get("ruta_picard", "")
        navegador = rutas_actuales.get("navegador", "edge")
        
        self.vista_utils.cargar_rutas(descarga, picard, navegador)
        self.vista_utils.vincular_guardado(self.guardar_rutas)

    def guardar_rutas(self):
        nuevas_rutas = self.vista_utils.obtener_rutas()
        self.modelo_viajero.guardar_rutas(nuevas_rutas)
        self.vista_utils.destroy()