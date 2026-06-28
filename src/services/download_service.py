import subprocess
import threading
import re

class ServicioDescarga:
    def ejecutar_descarga(self, enlace: str, calidad: str, ruta_destino: str, callback_progreso, callback_texto):
        hilo_descarga = threading.Thread(
            target=self._tarea_en_segundo_plano,
            args=(enlace, calidad, ruta_destino, callback_progreso, callback_texto),
            daemon=True
        )
        hilo_descarga.start()

    def _tarea_en_segundo_plano(self, enlace: str, calidad: str, ruta_destino: str, callback_progreso, callback_texto):
        callback_texto("Iniciando conexión con el servidor...")

        # Mapeo robusto de calidades con fallbacks
        argumentos_calidad = []
        if calidad == "Audio Rápido":
            argumentos_calidad = ["-f", "worstaudio/worst"]
        elif calidad == "Calidad Media":
            argumentos_calidad = ["-f", "bestaudio/best", "--audio-quality", "5"]
        else: # Máxima Calidad
            argumentos_calidad = ["-f", "bestaudio/best", "--audio-quality", "0"]
        
        comando = [
            "yt-dlp",
            "--no-update",             # Elimina la advertencia de 90 días
            "-x", "--audio-format", "mp3", # Fuerza la extracción a audio MP3
            *argumentos_calidad,
            "-P", ruta_destino,
            "--newline",
            enlace
        ]

        try:
            callback_texto(f"Ejecutando comando en: {ruta_destino}")
            proceso = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for linea in proceso.stdout:
                linea_limpia = linea.strip()
                if not linea_limpia: continue

                callback_texto(linea_limpia)

                patron_porcentaje = re.search(r'(\d+\.\d+)%', linea_limpia)
                if patron_porcentaje:
                    callback_progreso(float(patron_porcentaje.group(1)))

            proceso.wait()
            if proceso.returncode == 0:
                callback_texto("✔ Descarga completada con éxito.")
                callback_progreso(100.0)
            else:
                callback_texto(f"⚠ Ocurrió un error. Código de salida: {proceso.returncode}")

        except FileNotFoundError:
            callback_texto("Error Crítico: No se encontró el motor 'yt-dlp'.")
        except Exception as error:
            callback_texto(f"Error inesperado: {str(error)}")