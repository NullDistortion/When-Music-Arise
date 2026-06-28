"""
artist_model.py
---------------
Modelo exclusivo para la persistencia de estilos visuales en artist.json.
Responsabilidades: leer, escribir y validar la configuración de apariencia
(modo claro/oscuro, color de acento, tema de color).

No contiene lógica de negocio ni referencias a la vista.
"""

import json
import os
from typing import Dict, Any

# ── Ruta absoluta al archivo de persistencia ──────────────────────────────────
# __file__ → .../src/models/artist_model.py
# dirname  ×3 → raíz del proyecto (When_Music_Arise/)
_RUTA_MODULO = os.path.abspath(__file__)
_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(_RUTA_MODULO)))
RUTA_ARTIST_JSON = os.path.join(_RAIZ_PROYECTO, "basement", "artist.json")

# ── Valores predeterminados si artist.json no existe o está corrupto ──────────
ESTILOS_PREDETERMINADOS: Dict[str, Any] = {
    "modo_apariencia": "dark",       # "dark" | "light" | "system"
    "tema_color":      "green",      # "blue" | "green" | "dark-blue"
    "color_primario":  "#1DB954",    # Hex – color de acento para botones
    "fuente_principal": "Helvetica"  # Familia tipográfica base
}


class ArtistModel:
    """
    Gestiona la lectura y escritura del archivo artist.json.
    Toda la lógica de persistencia visual pasa exclusivamente por esta clase.
    """

    def __init__(self) -> None:
        # Garantiza que el directorio basement/ y artist.json existan al arrancar
        self._asegurar_archivo()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def leer_estilos(self) -> Dict[str, Any]:
        """
        Lee y retorna los estilos visuales desde artist.json.
        Si el archivo no existe o está corrompido, retorna los valores predeterminados.

        Returns:
            Dict con las claves: modo_apariencia, tema_color, color_primario, fuente_principal.
        """
        try:
            with open(RUTA_ARTIST_JSON, "r", encoding="utf-8") as archivo:
                datos_leidos = json.load(archivo)

            # Fusión defensiva: si faltan claves, se completan con los valores por defecto
            estilos_completos = {**ESTILOS_PREDETERMINADOS, **datos_leidos}
            return estilos_completos

        except (json.JSONDecodeError, FileNotFoundError, OSError):
            # El archivo está ausente o corrupto → restaurar valores por defecto
            self.guardar_estilos(ESTILOS_PREDETERMINADOS)
            return ESTILOS_PREDETERMINADOS.copy()

    def guardar_estilos(self, estilos: Dict[str, Any]) -> bool:
        """
        Escribe el diccionario de estilos completo en artist.json.

        Args:
            estilos: Diccionario con todos los pares clave/valor de apariencia.

        Returns:
            True si la escritura fue exitosa, False en caso contrario.
        """
        try:
            self._asegurar_directorio()
            with open(RUTA_ARTIST_JSON, "w", encoding="utf-8") as archivo:
                json.dump(estilos, archivo, indent=4, ensure_ascii=False)
            return True

        except (IOError, OSError) as error:
            print(f"[ArtistModel] Error al guardar estilos: {error}")
            return False

    def actualizar_campo(self, clave: str, valor: Any) -> bool:
        """
        Actualiza un único campo de estilos sin sobreescribir los demás.

        Args:
            clave:  Nombre del campo a actualizar (ej. "modo_apariencia").
            valor:  Nuevo valor para ese campo.

        Returns:
            True si la operación fue exitosa.
        """
        estilos_actuales = self.leer_estilos()
        estilos_actuales[clave] = valor
        return self.guardar_estilos(estilos_actuales)

    def restaurar_predeterminados(self) -> bool:
        """Sobreescribe artist.json con los valores de fábrica."""
        return self.guardar_estilos(ESTILOS_PREDETERMINADOS.copy())

    # ── Métodos privados ──────────────────────────────────────────────────────

    def _asegurar_directorio(self) -> None:
        """Crea el directorio basement/ si no existe."""
        directorio_basement = os.path.dirname(RUTA_ARTIST_JSON)
        os.makedirs(directorio_basement, exist_ok=True)

    def _asegurar_archivo(self) -> None:
        """Crea artist.json con valores predeterminados si no existe."""
        self._asegurar_directorio()
        if not os.path.exists(RUTA_ARTIST_JSON):
            self.guardar_estilos(ESTILOS_PREDETERMINADOS.copy())