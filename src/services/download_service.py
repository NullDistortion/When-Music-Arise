"""
download_service.py
-------------------
Servicio de descarga de música.
Responsabilidades:
  · Recibir un DTO con los datos de la descarga (enlace, calidad, rutas).
  · Ejecutar el motor CLI de descarga usando subprocess en un hilo separado (threading).
  · Emitir callbacks de progreso y finalización hacia el controlador.

REGLA ARQUITECTÓNICA: este módulo NO importa customtkinter ni ningún componente de vista.
Todo feedback a la interfaz se realiza exclusivamente a través de funciones callback.
"""

import os
import re
import subprocess
import threading
from typing import Callable, Dict, Optional


# ── Tipo de callbacks ──────────────────────────────────────────────────────────
# callback_progreso  → fn(texto: str, porcentaje: int)  – invocada por cada línea de salida
# callback_completado → fn(exito: bool, mensaje: str)   – invocada al terminar el proceso
TipoCallbackProgreso   = Callable[[str, int], None]
TipoCallbackCompletado = Callable[[bool, str], None]


class DownloadService:
    """
    Ejecuta el motor CLI de descarga de música en un hilo de fondo (daemon thread)
    para no bloquear el mainloop de la interfaz gráfica.

    Flujo de ejecución:
        1. iniciar_descarga()  → valida el DTO y lanza el hilo de fondo.
        2. _ejecutar_en_hilo() → corre en el hilo secundario; llama a subprocess.Popen.
        3. Lectura línea a línea de stdout → extrae porcentaje → dispara callback_progreso.
        4. Al terminar el proceso → dispara callback_completado con el código de retorno.
    """

    def __init__(self) -> None:
        # Referencia al proceso CLI activo (subprocess.Popen)
        self._proceso_activo: Optional[subprocess.Popen] = None

        # Referencia al hilo de descarga activo
        self._hilo_descarga: Optional[threading.Thread] = None

        # Bandera de estado (hilo-segura sólo para lectura simple)
        self._en_progreso: bool = False

    # ── API Pública ───────────────────────────────────────────────────────────

    def iniciar_descarga(
        self,
        dto_descarga: Dict[str, str],
        callback_progreso:   Optional[TipoCallbackProgreso]   = None,
        callback_completado: Optional[TipoCallbackCompletado] = None,
    ) -> bool:
        """
        Valida el DTO y lanza la descarga en un hilo secundario.

        Args:
            dto_descarga: {
                "enlace_musica":     str  – URL de la pista/álbum/lista.
                "calidad_audio":     str  – Bitrate deseado en kbps (ej. "320").
                "ruta_descarga":     str  – Directorio destino de los archivos.
                "ruta_descargador_cli": str – Ruta absoluta al ejecutable CLI.
            }
            callback_progreso:   Función llamada con (texto, porcentaje) por cada línea.
            callback_completado: Función llamada con (exito, mensaje) al terminar.

        Returns:
            True si el hilo fue iniciado con éxito; False si ya hay una descarga activa.
        """
        if self._en_progreso:
            return False

        # ── threading.Thread ──────────────────────────────────────────────────
        # Se usa un hilo demonio (daemon=True) para que, si el usuario cierra
        # la ventana principal, el hilo no impida que el proceso de Python termine.
        # La descarga corre en paralelo sin bloquear el mainloop de Tkinter/CTk.
        self._hilo_descarga = threading.Thread(
            target=self._ejecutar_en_hilo,
            args=(dto_descarga, callback_progreso, callback_completado),
            daemon=True,
            name="hilo-descarga-musica",
        )
        self._en_progreso = True
        self._hilo_descarga.start()
        return True

    def cancelar_descarga(self) -> bool:
        """
        Termina el proceso CLI activo enviándole la señal de terminación.

        Returns:
            True si había un proceso activo y fue terminado.
        """
        if self._proceso_activo and self._en_progreso:
            try:
                # subprocess.Popen.terminate() envía SIGTERM en Unix / TerminateProcess en Windows
                self._proceso_activo.terminate()
            except OSError:
                pass  # El proceso ya terminó por su cuenta
            self._en_progreso = False
            return True
        return False

    @property
    def en_progreso(self) -> bool:
        """Indica si hay una descarga activa en el hilo de fondo."""
        return self._en_progreso

    # ── Lógica interna (se ejecuta en el hilo secundario) ────────────────────

    def _ejecutar_en_hilo(
        self,
        dto_descarga:        Dict[str, str],
        callback_progreso:   Optional[TipoCallbackProgreso],
        callback_completado: Optional[TipoCallbackCompletado],
    ) -> None:
        """
        Método privado que corre en el hilo de fondo.
        Construye el comando CLI, abre el proceso con subprocess.Popen
        y lee su salida estándar en tiempo real.
        """
        # Desempaquetar el DTO (variables en español, según la especificación)
        enlace_musica      = dto_descarga.get("enlace_musica", "").strip()
        calidad_audio      = dto_descarga.get("calidad_audio", "320").strip()
        ruta_descarga      = dto_descarga.get("ruta_descarga", "").strip()
        ruta_descargador_cli = dto_descarga.get("ruta_descargador_cli", "").strip()

        # ── Validaciones previas a lanzar el proceso ──────────────────────────
        if not ruta_descargador_cli or not os.path.isfile(ruta_descargador_cli):
            self._finalizar(
                callback_completado,
                exito=False,
                mensaje=f"Descargador CLI no encontrado en: '{ruta_descargador_cli}'",
            )
            return

        if not os.path.isdir(ruta_descarga):
            try:
                os.makedirs(ruta_descarga, exist_ok=True)
            except OSError as error_dir:
                self._finalizar(
                    callback_completado,
                    exito=False,
                    mensaje=f"No se pudo crear el directorio de descarga: {error_dir}",
                )
                return

        # ── Construcción del comando CLI ──────────────────────────────────────
        # La estructura asume un descargador compatible con spotdl:
        #   spotdl <url> --output <dir> --bitrate <N>k
        # Puede adaptarse fácilmente a yt-dlp u otro motor en esta sección.
        comando_cli = [
            ruta_descargador_cli,
            enlace_musica,
            "--output",  f"{ruta_descarga}/{{title}}.{{output-ext}}",
            "--bitrate", f"{calidad_audio}k",
        ]

        try:
            # ── subprocess.Popen ──────────────────────────────────────────────
            # Abre el proceso CLI como subproceso hijo.
            # · stdout=subprocess.PIPE  → captura la salida estándar línea a línea.
            # · stderr=subprocess.STDOUT → redirige stderr al mismo pipe para lectura unificada.
            # · text=True               → decodifica bytes a str automáticamente.
            # · bufsize=1               → buffer de línea; asegura salida en tiempo real.
            # · encoding="utf-8"        → soporte de caracteres especiales en nombres de canciones.
            # · errors="replace"        → caracteres no decodificables se reemplazan por '?'.
            self._proceso_activo = subprocess.Popen(
                comando_cli,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                cwd=ruta_descarga,
            )

            # ── Lectura de salida en tiempo real ──────────────────────────────
            # self._proceso_activo.stdout es un iterador de líneas.
            # El bucle bloquea en el hilo secundario (no en el hilo principal).
            for linea_cruda in self._proceso_activo.stdout:
                linea = linea_cruda.strip()
                if linea and callback_progreso:
                    porcentaje_extraido = self._extraer_porcentaje(linea)
                    # El callback es invocado desde el hilo secundario.
                    # El controlador es responsable de usar .after() para
                    # actualizar la GUI de forma hilo-segura (thread-safe).
                    callback_progreso(linea, porcentaje_extraido)

            # ── Esperar que el proceso termine y obtener el código de salida ──
            # Popen.wait() bloquea hasta que el subproceso finaliza.
            codigo_retorno = self._proceso_activo.wait()
            exito   = (codigo_retorno == 0)
            mensaje = (
                "Descarga completada exitosamente."
                if exito
                else f"El proceso terminó con código de error: {codigo_retorno}"
            )
            self._finalizar(callback_completado, exito=exito, mensaje=mensaje)

        except FileNotFoundError:
            self._finalizar(
                callback_completado,
                exito=False,
                mensaje=f"No se encontró el ejecutable CLI en: '{ruta_descargador_cli}'",
            )
        except Exception as error_inesperado:
            self._finalizar(
                callback_completado,
                exito=False,
                mensaje=f"Error inesperado durante la descarga: {error_inesperado}",
            )

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _extraer_porcentaje(self, texto: str) -> int:
        """
        Intenta extraer un porcentaje numérico del texto de salida del CLI.
        Compatible con formatos de yt-dlp: '[download]  45.2% of ...'
        y formatos genéricos que contengan un número seguido de '%'.

        Returns:
            Entero entre 0 y 100, o 0 si no se detectó ningún porcentaje.
        """
        patron_porcentaje = r"(\d+(?:\.\d+)?)\s*%"
        coincidencias = re.findall(patron_porcentaje, texto)
        if coincidencias:
            try:
                return min(int(float(coincidencias[-1])), 100)
            except ValueError:
                return 0
        return 0

    def _finalizar(
        self,
        callback_completado: Optional[TipoCallbackCompletado],
        exito: bool,
        mensaje: str,
    ) -> None:
        """Restablece el estado y dispara el callback de finalización."""
        self._en_progreso    = False
        self._proceso_activo = None
        if callback_completado:
            callback_completado(exito, mensaje)