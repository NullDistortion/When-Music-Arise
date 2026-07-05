import subprocess
import os

class ServicioPicad:
    def abrir_programa(self, ruta_ejecutable: str, ruta_descargas: str):
        if not os.path.exists(ruta_ejecutable):
            return
            
        try:
            # Popen acepta múltiples argumentos. Al pasar la ruta_descargas,
            # Picard se abrirá cargando directamente ese directorio.
            argumentos = [ruta_ejecutable]
            if os.path.exists(ruta_descargas):
                argumentos.append(ruta_descargas)
                
            subprocess.Popen(argumentos)
            print(f"[PicadService] Ejecutando Picard en: {ruta_descargas}")
        except Exception as error:
            print(f"[Error PicadService] Fallo al intentar abrir Picard: {error}")