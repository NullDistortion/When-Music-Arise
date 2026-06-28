class ControladorPicad:
    def __init__(self, servicio_picad, modelo_viajero):
        self.servicio_picad = servicio_picad
        self.modelo_viajero = modelo_viajero

    def abrir_picard(self):
        rutas = self.modelo_viajero.leer_rutas()
        ruta_ejecutable = rutas.get("ruta_picard", "")

        if not ruta_ejecutable:
            print("[SISTEMA] Error: La ruta de Picard no está configurada en Traveller.")
            return

        self.servicio_picad.abrir_programa(ruta_ejecutable)