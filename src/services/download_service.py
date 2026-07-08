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
        errores_detectados = [] 
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
            callback_fin(False, errores_detectados)
            return

        comando = [
            ruta_ytdlp, "--no-update", "-x", "--audio-format", "mp3",
            "--output", f"{ruta_destino}/%(title)s.%(ext)s",
            "--replace-in-metadata", "title", r"(?i)\s*[\(\[].*?(?:official|music|video|audio|lyric).*?[\)\]]\s*", "",
            *argumentos_calidad, "--newline", enlace
        ]

        try:
            self.proceso = subprocess.Popen(comando, **opciones_proceso)
            
            pista_actual = "Pista Individual"
            id_actual = ""

            for linea in self.proceso.stdout:
                while self.pausado:
                    time.sleep(0.5)
                if self.cancelado:
                    break

                linea_limpia = linea.strip()
                if not linea_limpia: continue

                # 1. Rastrear posición en la playlist
                match_item = re.search(r'Downloading item (\d+ of \d+)', linea_limpia)
                if match_item:
                    pista_actual = f"Pista {match_item.group(1)}"

                # 2. Rastrear ID del video actual
                match_url = re.search(r'watch\?v=([a-zA-Z0-9_-]+)', linea_limpia)
                if match_url:
                    id_actual = match_url.group(1)

                # 3. Capturar y traducir el error
                if linea_limpia.startswith("ERROR:"):
                    motivo = "Error desconocido de descarga"
                    str_lower = linea_limpia.lower()
                    
                    if "sign in to confirm your age" in str_lower:
                        motivo = "Restricción de edad (+18)"
                    elif "private video" in str_lower:
                        motivo = "Video privado"
                    elif "unavailable" in str_lower:
                        motivo = "Video no disponible / Eliminado"
                    elif "members-only" in str_lower:
                        motivo = "Video exclusivo para miembros"

                    enlace_fallido = f"https://youtube.com/watch?v={id_actual}" if id_actual else "Enlace desconocido"
                    
                    mensaje_amigable = f"{pista_actual} -> {motivo}\n   Link: {enlace_fallido}"
                    
                    if mensaje_amigable not in errores_detectados:
                        errores_detectados.append(mensaje_amigable)

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
                exito_operacion = True

        except Exception as error:
            error_str = f"Error inesperado: {str(error)}"
            callback_texto(error_str)
            errores_detectados.append(error_str)
        finally:
            callback_fin(exito_operacion, errores_detectados)