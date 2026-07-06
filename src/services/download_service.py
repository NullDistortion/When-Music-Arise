import subprocess
import threading
import re
import time

class ServicioDescarga:
    def __init__(self):
        self.proceso = None
        self.pausado = False
        self.cancelado = False

    def pausar_descarga(self): self.pausado = True
    def reanudar_descarga(self): self.pausado = False
    
    def cancelar_descarga(self):
        self.cancelado = True
        self.pausado = False 
        if self.proceso:
            self.proceso.terminate()

    def ejecutar_descarga(self, enlace: str, calidad: str, ruta_destino: str, callback_progreso, callback_texto, callback_fin):
        self.pausado = False
        self.cancelado = False
        
        hilo_descarga = threading.Thread(
            target=self._tarea_en_segundo_plano,
            args=(enlace, calidad, ruta_destino, callback_progreso, callback_texto, callback_fin),
            daemon=True
        )
        hilo_descarga.start()

    def _tarea_en_segundo_plano(self, enlace: str, calidad: str, ruta_destino: str, callback_progreso, callback_texto, callback_fin):
        exito_operacion = False
        callback_texto("Iniciando conexión con el servidor...")

        argumentos_calidad = []
        if calidad == "Audio Rápido": argumentos_calidad = ["-f", "worstaudio/worst"]
        elif calidad == "Calidad Media": argumentos_calidad = ["-f", "bestaudio/best", "--audio-quality", "5"]
        else: argumentos_calidad = ["-f", "bestaudio/best", "--audio-quality", "0"]
        
        comando = [
            "yt-dlp", "--no-update", "-x", "--audio-format", "mp3",
            "--output", f"{ruta_destino}/%(title)s.%(ext)s",
            "--replace-in-metadata", "title", r"(?i)\s*[\(\[].*?(?:official|music|video|audio|lyric).*?[\)\]]\s*", "",
            *argumentos_calidad, "--newline", enlace
        ]

        try:
            callback_texto(f"Ejecutando comando...")
            self.proceso = subprocess.Popen(
                comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )

            for linea in self.proceso.stdout:
                # Sistema de Pausa Inteligente
                while self.pausado:
                    time.sleep(0.5)
                if self.cancelado:
                    break

                linea_limpia = linea.strip()
                if not linea_limpia: continue
                callback_texto(linea_limpia)

                patron_porcentaje = re.search(r'(\d+\.\d+)%', linea_limpia)
                if patron_porcentaje:
                    callback_progreso(float(patron_porcentaje.group(1)))

            self.proceso.wait()
            
            if self.cancelado:
                pass # El gestor se encarga del mensaje
            elif self.proceso.returncode == 0:
                callback_texto("✔ Descarga y limpieza completada con éxito.")
                callback_progreso(100.0)
                exito_operacion = True
            else:
                callback_texto(f"⚠ Ocurrió un error o advertencia. Código: {self.proceso.returncode}")
                # Forzamos el éxito a True para que Picard abra igual tras playlists con avisos
                exito_operacion = True 

        except FileNotFoundError:
            callback_texto("Error Crítico: No se encontró el motor 'yt-dlp'.")
        except Exception as error:
            callback_texto(f"Error inesperado: {str(error)}")
        finally:
            callback_fin(exito_operacion)