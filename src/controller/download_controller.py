"""
download_controller.py
----------------------
Controlador de descarga de música.
Responsabilidades:
  · Capturar los datos de la vista (enlace, calidad).
  · Validar el formato del enlace antes de despachar.
  · Construir el DTO de descarga con las rutas del ConfigController.
  · Despachar al DownloadService y convertir sus callbacks en actualizaciones
    de GUI hilo-seguras mediante CTk's .after(0, ...).
"""

import re
from typing import Optional

from src.services.download_service import DownloadService

# ── Patrón de validación de URL ───────────────────────────────────────────────
# Acepta URLs http y https con dominio, IP o localhost.
_PATRON_URL_VALIDA = re.compile(
    r"^https?://"                                          # Esquema
    r"(?:"
    r"  (?:[A-Z0-9](?:[A-Z0-9\-]{0,61}[A-Z0-9])?\.)"    # Subdominio(s)
    r"  +[A-Z]{2,6}\.?"                                   # TLD
    r"  |localhost"                                        # O localhost
    r"  |\d{1,3}(?:\.\d{1,3}){3}"                        # O dirección IP
    r")"
    r"(?::\d+)?"                                          # Puerto opcional
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE | re.VERBOSE,
)


class DownloadController:
    """
    Orquesta el ciclo completo de una descarga:
    validación → construcción del DTO → despacho al servicio → actualización de la GUI.
    """

    def __init__(self, vista, controlador_principal) -> None:
        self._servicio_descarga     = DownloadService()
        self._vista                 = vista       # main_view (CTk root window)
        self._controlador_principal = controlador_principal

    # ── API Pública ───────────────────────────────────────────────────────────

    def iniciar_descarga(self, enlace_musica: str, calidad_audio: str) -> None:
        """
        Punto de entrada llamado por la vista cuando el usuario pulsa 'Descargar'.

        Args:
            enlace_musica: URL del contenido a descargar (pista, álbum o lista).
            calidad_audio: Bitrate en kbps como cadena (ej. "320").
        """
        # 1. Validar el enlace
        if not self._validar_enlace(enlace_musica):
            self._vista.mostrar_error(
                "Enlace no válido.\n"
                "Ingresa una URL completa (ej. https://open.spotify.com/track/...)."
            )
            return

        # 2. Verificar que no haya una descarga activa
        if self._servicio_descarga.en_progreso:
            self._vista.mostrar_error(
                "Ya hay una descarga en curso. "
                "Espera a que termine o cancélala antes de iniciar otra."
            )
            return

        # 3. Obtener rutas desde ConfigController (sin acceder al disco directamente)
        controlador_config = self._controlador_principal.obtener_controlador("config")
        ruta_descarga       = controlador_config.obtener_ruta_descarga()       if controlador_config else ""
        ruta_descargador_cli = controlador_config.obtener_ruta_descargador_cli() if controlador_config else ""

        if not ruta_descargador_cli:
            self._vista.mostrar_error(
                "El descargador CLI no está configurado.\n"
                "Ve a ⚙ Config → 'Ruta del descargador CLI'."
            )
            return

        # 4. Construir el DTO de descarga (variables en español, según especificación)
        dto_descarga = {
            "enlace_musica":       enlace_musica.strip(),
            "calidad_audio":       calidad_audio.strip(),
            "ruta_descarga":       ruta_descarga,
            "ruta_descargador_cli": ruta_descargador_cli,
        }

        # 5. Actualizar estado de la GUI antes de lanzar el hilo
        self._vista.mostrar_log(f"Iniciando descarga: {enlace_musica}")
        self._vista.actualizar_estado_descarga(en_progreso=True)

        # 6. Despachar al servicio (lanza el hilo de fondo)
        self._servicio_descarga.iniciar_descarga(
            dto_descarga=dto_descarga,
            callback_progreso=self._al_recibir_progreso,
            callback_completado=self._al_completar_descarga,
        )

    def cancelar_descarga(self) -> None:
        """Solicita la cancelación de la descarga activa."""
        exito_cancelacion = self._servicio_descarga.cancelar_descarga()
        if exito_cancelacion:
            self._vista.mostrar_log("Descarga cancelada por el usuario.")
            self._vista.actualizar_estado_descarga(en_progreso=False)

    # ── Callbacks del servicio (se invocan desde el hilo secundario) ──────────

    def _al_recibir_progreso(self, texto: str, porcentaje: int) -> None:
        """
        Callback invocado por DownloadService desde el hilo de descarga
        cada vez que el proceso CLI emite una línea de salida.

        IMPORTANTE – seguridad de hilos (thread-safety):
        Tkinter/CustomTkinter NO es hilo-seguro. Modificar widgets desde
        un hilo secundario puede corromper el estado de la GUI o generar
        excepciones silenciosas.

        Solución: self._vista.after(0, fn) encola la actualización en el
        hilo principal (mainloop). El '0' indica "ejecutar lo antes posible
        en el siguiente ciclo del event loop", sin introducir retardo perceptible.
        """
        self._vista.after(
            0,
            lambda t=texto, p=porcentaje: self._vista.mostrar_progreso(t, p)
        )

    def _al_completar_descarga(self, exito: bool, mensaje: str) -> None:
        """
        Callback invocado por DownloadService desde el hilo de descarga
        cuando el proceso CLI termina (con éxito o con error).

        Al igual que _al_recibir_progreso, usa .after(0, ...) para
        garantizar que la actualización de la GUI ocurra en el hilo principal.
        """
        def _actualizar_gui_al_terminar():
            self._vista.mostrar_log(mensaje)
            self._vista.actualizar_estado_descarga(en_progreso=False)
            if exito:
                # Asegurar que la barra de progreso llegue a 100% al finalizar
                self._vista.mostrar_progreso("Descarga completada.", 100)

        # Encolar actualización en el hilo principal del event loop
        self._vista.after(0, _actualizar_gui_al_terminar)

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _validar_enlace(self, enlace: str) -> bool:
        """
        Verifica que el enlace sea una URL HTTP/HTTPS bien formada.

        Args:
            enlace: Cadena a validar.

        Returns:
            True si el enlace es una URL válida, False en caso contrario.
        """
        if not enlace or not enlace.strip():
            return False
        return bool(_PATRON_URL_VALIDA.match(enlace.strip()))