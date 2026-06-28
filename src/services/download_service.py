import subprocess
import threading
import re

class ServicioDescarga:
    """Se comunica con el motor CLI de descarga en segundo plano."""

    def ejecutar_descarga(self, enlace: str, calidad: str, ruta_destino: str, callback_progreso, callback_texto):
        """
        Punto de entrada llamado por el Controlador. 
        Despierta un hilo esclavo (daemon) para evitar que la interfaz gráfica se congele.
        """
        hilo_descarga = threading.Thread(
            target=self._tarea_en_segundo_plano,
            args=(enlace, calidad, ruta_destino, callback_progreso, callback_texto),
            daemon=True  # El hilo muere automáticamente si se cierra la app principal
        )
        hilo_descarga.start()

    def _tarea_en_segundo_plano(self, enlace: str, calidad: str, ruta_destino: str, callback_progreso, callback_texto):
        """
        Esta función se ejecuta fuera del hilo principal (GUI).
        """
        callback_texto("Iniciando conexión con el servidor...")

        # ----------------------------------------------------------------------
        # Mapeo de calidades a parámetros del CLI (Ajusta según tu motor específico)
        # ----------------------------------------------------------------------
        argumentos_calidad = []
        if calidad == "Audio Rápido":
            argumentos_calidad = ["-f", "worstaudio"]
        elif calidad == "Máxima Calidad":
            argumentos_calidad = ["-f", "bestaudio"]
        
        # ----------------------------------------------------------------------
        # Construcción del comando. (Ejemplo usando yt-dlp como motor estándar)
        # IMPORTANTE: Reemplaza "yt-dlp" por el nombre de tu motor CLI real.
        # ----------------------------------------------------------------------
        comando = [
            "yt-dlp",
            *argumentos_calidad,
            "-P", ruta_destino,  # Ruta donde se guardará el archivo
            "--newline",         # Fuerza la salida línea por línea para leerla fácilmente
            enlace
        ]

        try:
            callback_texto(f"Ejecutando comando en: {ruta_destino}")
            
            # subprocess.Popen con stdout=PIPE permite capturar lo que el motor CLI
            # escribe en la consola en tiempo real.
            proceso = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW # Evita que salte una ventana negra de CMD en Windows
            )

            # Leer la consola del CLI línea por línea mientras se ejecuta
            for linea in proceso.stdout:
                linea_limpia = linea.strip()
                if not linea_limpia:
                    continue

                # 1. Enviar el texto completo a la vista tradicional (Consola)
                callback_texto(linea_limpia)

                # 2. Extraer el porcentaje con Expresiones Regulares para la vista moderna
                # Busca patrones como " 45.5%" o "[download] 10.0%"
                patron_porcentaje = re.search(r'(\d+\.\d+)%', linea_limpia)
                if patron_porcentaje:
                    porcentaje_float = float(patron_porcentaje.group(1))
                    callback_progreso(porcentaje_float)

            # Esperar a que el proceso termine y verificar su estado
            proceso.wait()
            if proceso.returncode == 0:
                callback_texto("✔ Descarga completada con éxito.")
                callback_progreso(100.0)
            else:
                callback_texto(f"⚠ Ocurrió un error. Código de salida: {proceso.returncode}")

        except FileNotFoundError:
            callback_texto("Error Crítico: No se encontró el motor de descarga CLI.")
            callback_texto("Asegúrate de que el ejecutable esté en la carpeta del proyecto o en el PATH del sistema.")
        except Exception as error:
            callback_texto(f"Error inesperado durante la descarga: {str(error)}")