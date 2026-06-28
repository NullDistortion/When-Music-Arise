"""
config_controller.py
--------------------
Controlador de configuración de rutas locales.
Responsabilidades:
  · Conectar UtilsView con TravellerModel.
  · Abrir/gestionar la ventana de configuración de rutas (Traveller).
  · Proveer getters semánticos de rutas para los demás controladores.
"""

from typing import Any, Dict, Optional


class ConfigController:
    """
    Puente entre la vista de configuración (UtilsView) y el modelo de rutas (TravellerModel).
    """

    def __init__(self, controlador_principal) -> None:
        from src.models.traveller_model import TravellerModel

        self._modelo_traveller      = TravellerModel()
        self._controlador_principal = controlador_principal

        # Referencia a la ventana auxiliar abierta
        self._ventana_utils: Optional[Any] = None

    # ── Apertura de ventana ───────────────────────────────────────────────────

    def abrir_ventana_configuracion(self) -> None:
        """
        Abre UtilsView con las rutas actuales precargadas.
        Si la ventana ya está abierta, la trae al frente.
        """
        from src.view.utils_view import UtilsView

        if self._ventana_utils is not None:
            try:
                if self._ventana_utils.winfo_exists():
                    self._ventana_utils.focus()
                    return
            except Exception:
                pass

        rutas_actuales = self._modelo_traveller.leer_rutas()

        self._ventana_utils = UtilsView(
            controlador=self,
            rutas_actuales=rutas_actuales,
        )

    # ── Operaciones de datos ──────────────────────────────────────────────────

    def leer_rutas_actuales(self) -> Dict[str, Any]:
        """
        Retorna las rutas almacenadas en traveller.json.
        Llamado por UtilsView para precargar los campos del formulario.
        """
        return self._modelo_traveller.leer_rutas()

    def guardar_rutas(self, nuevas_rutas: Dict[str, str]) -> bool:
        """
        Persiste las nuevas rutas en traveller.json.

        Args:
            nuevas_rutas: Diccionario con los pares clave/ruta a guardar.

        Returns:
            True si la operación fue exitosa.
        """
        return self._modelo_traveller.guardar_rutas(nuevas_rutas)

    # ── Getters semánticos (usados por DownloadController y PicadController) ──

    def obtener_ruta_descarga(self) -> str:
        """Retorna el directorio destino para los archivos descargados."""
        return self._modelo_traveller.obtener_ruta_descarga()

    def obtener_ruta_picard(self) -> str:
        """Retorna la ruta al ejecutable de MusicBrainz Picard."""
        return self._modelo_traveller.obtener_ruta_picard()

    def obtener_ruta_descargador_cli(self) -> str:
        """Retorna la ruta al ejecutable del motor CLI de descarga."""
        return self._modelo_traveller.obtener_ruta_descargador_cli()

    def rutas_listas(self) -> bool:
        """
        Verifica que las rutas mínimas para operar estén configuradas.
        Útil para mostrar un aviso al usuario en el arranque.
        """
        return self._modelo_traveller.rutas_minimas_configuradas()