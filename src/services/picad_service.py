import subprocess
import os

class ServicioPicad:
    """Lanza el ejecutable externo MusicBrainz Picard."""

    def abrir_programa(self, ruta_ejecutable: str):
        if not os.path.exists(ruta_ejecutable):
            print(f"[Error PicadService] La ruta especificada no existe: {ruta_ejecutable}")
            return
            
        try:
            # subprocess.Popen lanza el proceso externo y devuelve el control a Python inmediatamente.
            # No bloquea la ejecución de nuestra aplicación.
            subprocess.Popen([ruta_ejecutable])
            print(f"[PicadService] Ejecutando: {ruta_ejecutable}")
        except Exception as error:
            print(f"[Error PicadService] Fallo al intentar abrir el programa: {error}")