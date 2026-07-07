import subprocess
import threading
import re
import time
import os
import sys

from src.utils.path_helper import obtener_ruta_absoluta

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

    def ejecutar_descarga(self, enlace: str, calidad: str, ruta_destino: str, ruta_cookies: str, callback_progreso, callback_texto, callback_fin):
        self.pausado = False
        self.cancelado = False
        
        hilo_descarga = threading.Thread(
            target=self._tarea_en_segundo_plano,
            args=(enlace, calidad, ruta_destino, ruta_cookies, callback_progreso, callback_texto, callback_fin),
            daemon=True
        )
        hilo_descarga.start()

    def _tarea_en_segundo_plano(self, enlace: str, calidad: str, ruta_destino: str, ruta_cookies: str, callback_progreso, callback_texto, callback_fin):
        exito_operacion = False
        callback_texto("Iniciando conexión con el servidor...")

        argumentos_calidad = []
        if calidad == "Audio Rápido": argumentos_calidad = ["-f", "worstaudio/worst"]
        elif calidad == "Calidad Media": argumentos_calidad = ["-f", "bestaudio/best", "--audio-quality", "5"]
        else: argumentos_calidad = ["-f", "bestaudio/best", "--audio-quality", "0"]
        
        nombre_ytdlp = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"
        ruta_ytdlp = obtener_ruta_absoluta(os.path.join("bin", nombre_ytdlp))

        opciones_proceso = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True
        }
        if sys.platform == "win32":
            opciones_proceso["creationflags"] = subprocess.CREATE_NO_WINDOW

        if not os.path.exists(ruta_ytdlp):
            callback_texto(f"Error Crítico: No se encontró el motor en {ruta_ytdlp}")
            callback_fin(False)
            return

        # LOGICA DE COOKIES VÍA ARCHIVO
        argumentos_cookies = []
        if ruta_cookies and os.path.exists(ruta_cookies):
            callback_texto("Aplicando archivo de cookies externo para autorización...")
            argumentos_cookies = ["--cookies", ruta_cookies]
        else:
            callback_texto("Intentando extracción pública estándar...")

        comando = [
            ruta_ytdlp, "--no-update", "-x", "--audio-format", "mp3",
            *argumentos_cookies,
            "--output", f"{ruta_destino}/%(title)s.%(ext)s",
            "--replace-in-metadata", "title", r"(?i)\s*[\(\[].*?(?:official|music|video|audio|lyric).*?[\)\]]\s*", "",
            *argumentos_calidad, "--newline", enlace
        ]

        try:
            self.proceso = subprocess.Popen(comando, **opciones_proceso)

            for linea in self.proceso.stdout:
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
                pass 
            elif self.proceso.returncode == 0:
                callback_texto("✔ Descarga completada con éxito.")
                callback_progreso(100.0)
                exito_operacion = True
            else:
                callback_texto(f"⚠ Ocurrió un error o advertencia. Código: {self.proceso.returncode}")
                exito_operacion = True # Fuerza la apertura de Picard si la playlist fue parcial

        except Exception as error:
            callback_texto(f"Error inesperado: {str(error)}")
        finally:
            callback_fin(exito_operacion)