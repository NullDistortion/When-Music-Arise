import subprocess
import os
import sys

class ServicioPicad:

    def abrir_programa(self, ruta_ejecutable: str, ruta_descargas: str):
        if not os.path.exists(ruta_ejecutable):
            print(f"[Error PicadService] La ruta especificada no existe: {ruta_ejecutable}")
            return
            
        try:
            argumentos = [ruta_ejecutable]
            if os.path.exists(ruta_descargas):
                argumentos.append(ruta_descargas)

            if sys.platform == "win32":
                # DETACHED_PROCESS = 0x00000008
                # CREATE_NEW_PROCESS_GROUP = 0x00000200
                flags = 0x00000008 | 0x00000200
                
                subprocess.Popen(
                    argumentos,
                    creationflags=flags,
                    close_fds=True # Cierra los flujos de texto heredados
                )
            else:
                subprocess.Popen(
                    argumentos,
                    start_new_session=True,
                    close_fds=True
                )
            
            print(f"[PicadService] Ejecutando Picard en: {ruta_descargas}")
            
        except Exception as error:
            print(f"[Error PicadService] Fallo al intentar abrir Picard: {error}")