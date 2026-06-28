"""
picad_service.py
----------------
Servicio de integración con MusicBrainz Picard.
Responsabilidades:
  · Recibir la ruta al ejecutable de Picard.
  · Abrir Picard como proceso independiente usando subprocess.Popen.
  · Retornar una tupla (exito, mensaje) sin bloquear la GUI.

REGLA ARQUITECTÓNICA: este módulo NO importa customtkinter ni ningún componente de vista.
"""

import os
import subprocess
from typing import Optional, Tuple


class PicadService:
    """
    Lanza MusicBrainz Picard como un proceso hijo independiente.

    Picard se ejecuta de forma autónoma: la aplicación no espera a que termine
    (a diferencia del motor de descarga). Esto permite al usuario trabajar
    en When Music Arise mientras Picard está abierto en paralelo.
    """

    def __init__(self) -> None:
        # Referencia opcional al proceso de Picard para consultar su estado
        self._proceso_picard: Optional[subprocess.Popen] = None

    # ── API Pública ───────────────────────────────────────────────────────────

    def abrir_picard(self, ruta_picard: str) -> Tuple[bool, str]:
        """
        Abre el ejecutable de MusicBrainz Picard.

        Args:
            ruta_picard: Ruta absoluta al archivo .exe (o binario) de Picard.

        Returns:
            Tupla (exito: bool, mensaje: str).
            · exito=True  → Picard se inició correctamente.
            · exito=False → Se retorna el motivo del fallo en 'mensaje'.
        """
        # ── Validaciones previas ──────────────────────────────────────────────
        if not ruta_picard or not ruta_picard.strip():
            return False, "La ruta de MusicBrainz Picard no está configurada."

        ruta_picard = ruta_picard.strip()

        if not os.path.isfile(ruta_picard):
            return False, (
                f"No se encontró el ejecutable de Picard en:\n'{ruta_picard}'"
            )

        # Si Picard ya está corriendo, no abrir una segunda instancia
        if self.esta_ejecutando():
            return False, "MusicBrainz Picard ya está abierto."

        try:
            # ── subprocess.Popen ──────────────────────────────────────────────
            # Se usa Popen (NO subprocess.run / subprocess.call) porque:
            # · Popen no bloquea: retorna inmediatamente y la GUI sigue respondiendo.
            # · El proceso hijo (Picard) vive de forma autónoma, independientemente
            #   de When Music Arise.
            #
            # · stdout=subprocess.DEVNULL → se descarta la salida de Picard;
            #   no necesitamos leerla.
            # · stderr=subprocess.DEVNULL → ídem para errores de Picard.
            # · cwd=directorio del .exe   → Picard puede necesitar su directorio
            #   de trabajo para cargar recursos relativos.
            directorio_picard = os.path.dirname(ruta_picard)

            self._proceso_picard = subprocess.Popen(
                [ruta_picard],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=directorio_picard if directorio_picard else None,
            )
            return True, "MusicBrainz Picard iniciado correctamente."

        except PermissionError:
            return False, (
                "Permiso denegado. Verifica que tienes permisos de ejecución "
                "para el archivo de Picard."
            )
        except OSError as error_os:
            return False, f"Error del sistema operativo al abrir Picard: {error_os}"
        except Exception as error_inesperado:
            return False, f"Error inesperado al abrir Picard: {error_inesperado}"

    def esta_ejecutando(self) -> bool:
        """
        Verifica si el proceso de Picard lanzado por este servicio sigue activo.

        Returns:
            True si Picard está corriendo; False si terminó o nunca fue iniciado.
        """
        if self._proceso_picard is None:
            return False
        # poll() retorna None si el proceso todavía está en ejecución,
        # o el código de retorno (int) si ya terminó.
        return self._proceso_picard.poll() is None

    def cerrar_picard(self) -> bool:
        """
        Solicita el cierre del proceso de Picard gestionado por este servicio.

        Returns:
            True si se envió la señal de terminación; False si no había proceso activo.
        """
        if self.esta_ejecutando() and self._proceso_picard:
            try:
                self._proceso_picard.terminate()
            except OSError:
                pass
            return True
        return False