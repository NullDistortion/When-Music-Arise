"""
traveller_model.py
------------------
Modelo exclusivo para la persistencia de rutas locales en traveller.json.
Responsabilidades: leer, escribir y proveer las rutas de:
  · Directorio de descarga de música.
  · Ejecutable del motor CLI de descarga.
  · Ejecutable de MusicBrainz Picard.

No contiene lógica de negocio ni referencias a la vista.
"""

import json
import os
from typing import Dict, Any

# ── Ruta absoluta al archivo de persistencia ──────────────────────────────────
# __file__ → .../src/models/traveller_model.py
# dirname  ×3 → raíz del proyecto (When_Music_Arise/)
_RUTA_MODULO   = os.path.abspath(__file__)
_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(_RUTA_MODULO)))
RUTA_TRAVELLER_JSON = os.path.join(_RAIZ_PROYECTO, "basement", "traveller.json")

# ── Valores predeterminados ───────────────────────────────────────────────────
RUTAS_PREDETERMINADAS: Dict[str, str] = {
    # Directorio donde se guardarán los archivos de audio descargados
    "ruta_descarga":        os.path.join(os.path.expanduser("~"), "Music"),
    # Ruta completa al ejecutable del descargador CLI (ej. spotdl.exe, yt-dlp.exe)
    "ruta_descargador_cli": "",
    # Ruta completa al ejecutable de MusicBrainz Picard
    "ruta_picard":          ""
}


class TravellerModel:
    """
    Gestiona la lectura y escritura del archivo traveller.json.
    Toda la lógica de persistencia de rutas locales pasa por esta clase.
    """

    def __init__(self) -> None:
        # Garantiza que el directorio basement/ y traveller.json existan al arrancar
        self._asegurar_archivo()

    # ── Métodos públicos – Operaciones completas ──────────────────────────────

    def leer_rutas(self) -> Dict[str, str]:
        """
        Lee y retorna todas las rutas desde traveller.json.
        Si el archivo no existe o está corrompido, retorna los valores predeterminados.

        Returns:
            Dict con las claves: ruta_descarga, ruta_descargador_cli, ruta_picard.
        """
        try:
            with open(RUTA_TRAVELLER_JSON, "r", encoding="utf-8") as archivo:
                datos_leidos = json.load(archivo)

            # Fusión defensiva: claves faltantes se completan con predeterminados
            rutas_completas = {**RUTAS_PREDETERMINADAS, **datos_leidos}
            return rutas_completas

        except (json.JSONDecodeError, FileNotFoundError, OSError):
            self.guardar_rutas(RUTAS_PREDETERMINADAS)
            return RUTAS_PREDETERMINADAS.copy()

    def guardar_rutas(self, rutas: Dict[str, str]) -> bool:
        """
        Escribe el diccionario de rutas completo en traveller.json.

        Args:
            rutas: Diccionario con todos los pares clave/ruta.

        Returns:
            True si la escritura fue exitosa, False en caso contrario.
        """
        try:
            self._asegurar_directorio()
            with open(RUTA_TRAVELLER_JSON, "w", encoding="utf-8") as archivo:
                json.dump(rutas, archivo, indent=4, ensure_ascii=False)
            return True

        except (IOError, OSError) as error:
            print(f"[TravellerModel] Error al guardar rutas: {error}")
            return False

    def actualizar_ruta(self, clave: str, nueva_ruta: str) -> bool:
        """
        Actualiza una única ruta sin sobreescribir las demás.

        Args:
            clave:      Nombre del campo (ej. "ruta_descarga").
            nueva_ruta: Valor de la nueva ruta.

        Returns:
            True si la operación fue exitosa.
        """
        rutas_actuales = self.leer_rutas()
        rutas_actuales[clave] = nueva_ruta
        return self.guardar_rutas(rutas_actuales)

    # ── Métodos de acceso rápido (getters semánticos) ─────────────────────────

    def obtener_ruta_descarga(self) -> str:
        """Retorna el directorio de destino para las descargas."""
        return self.leer_rutas().get("ruta_descarga", RUTAS_PREDETERMINADAS["ruta_descarga"])

    def obtener_ruta_picard(self) -> str:
        """Retorna la ruta al ejecutable de MusicBrainz Picard."""
        return self.leer_rutas().get("ruta_picard", "")

    def obtener_ruta_descargador_cli(self) -> str:
        """Retorna la ruta al ejecutable del motor CLI de descarga."""
        return self.leer_rutas().get("ruta_descargador_cli", "")

    def rutas_minimas_configuradas(self) -> bool:
        """
        Valida que las rutas mínimas requeridas para operar estén configuradas.

        Returns:
            True si ruta_descarga y ruta_descargador_cli están definidas.
        """
        rutas = self.leer_rutas()
        ruta_descarga_ok = bool(rutas.get("ruta_descarga", "").strip())
        ruta_cli_ok      = bool(rutas.get("ruta_descargador_cli", "").strip())
        return ruta_descarga_ok and ruta_cli_ok

    # ── Métodos privados ──────────────────────────────────────────────────────

    def _asegurar_directorio(self) -> None:
        """Crea el directorio basement/ si no existe."""
        directorio_basement = os.path.dirname(RUTA_TRAVELLER_JSON)
        os.makedirs(directorio_basement, exist_ok=True)

    def _asegurar_archivo(self) -> None:
        """Crea traveller.json con valores predeterminados si no existe."""
        self._asegurar_directorio()
        if not os.path.exists(RUTA_TRAVELLER_JSON):
            self.guardar_rutas(RUTAS_PREDETERMINADAS.copy())