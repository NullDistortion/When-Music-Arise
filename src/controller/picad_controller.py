import tkinter.messagebox as messagebox

class ControladorPicad:
    def __init__(self, servicio_picad, modelo_viajero):
        self.servicio_picad = servicio_picad
        self.modelo_viajero = modelo_viajero

    def abrir_picard(self):
        rutas = self.modelo_viajero.leer_rutas()
        ruta_ejecutable = rutas.get("ruta_picard", "").strip()
        ruta_descargas = rutas.get("ruta_descarga", "").strip()

        if not ruta_ejecutable:
            messagebox.showwarning(
                "Advertencia de Picard", 
                "No se ha configurado la ruta de MusicBrainz Picard.\n\nPor favor, dirígete a 'Rutas (Traveller)'."
            )
            return

        self.servicio_picad.abrir_programa(ruta_ejecutable, ruta_descargas)