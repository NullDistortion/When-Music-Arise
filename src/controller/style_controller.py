"""
style_controller.py
-------------------
Controlador de estilos visuales.
Responsabilidades:
  · Conectar DavinciView con ArtistModel.
  · Abrir/gestionar la ventana de personalización visual.
  · Solicitar la lectura de estilos actuales al modelo.
  · Guardar nuevos estilos a través del modelo y notificar al MainController.
"""

from typing import Any, Dict, Optional


class StyleController:
    """
    Puente entre la vista de estilos (DavinciView) y el modelo de persistencia (ArtistModel).
    No contiene lógica de negocio visual; sólo orquesta el flujo de datos.
    """

    def __init__(self, controlador_principal) -> None:
        from src.models.artist_model import ArtistModel

        self._modelo_artista    = ArtistModel()
        self._controlador_principal = controlador_principal

        # Referencia a la ventana auxiliar abierta (para evitar duplicados)
        self._ventana_davinci: Optional[Any] = None

    # ── Apertura de ventana ───────────────────────────────────────────────────

    def abrir_ventana_estilos(self) -> None:
        """
        Abre la ventana DavinciView con los estilos actuales precargados.
        Si la ventana ya está abierta, la trae al frente.
        """
        from src.view.davinci_view import DavinciView

        # Evitar abrir múltiples instancias simultáneas
        if self._ventana_davinci is not None:
            try:
                if self._ventana_davinci.winfo_exists():
                    self._ventana_davinci.focus()
                    return
            except Exception:
                pass  # La ventana fue destruida externamente

        estilos_actuales = self._modelo_artista.leer_estilos()

        self._ventana_davinci = DavinciView(
            controlador=self,
            estilos_actuales=estilos_actuales,
        )

    # ── Operaciones de datos ──────────────────────────────────────────────────

    def leer_estilos_actuales(self) -> Dict[str, Any]:
        """
        Retorna los estilos almacenados en artist.json.
        Llamado por DavinciView para precargar los campos del formulario.
        """
        return self._modelo_artista.leer_estilos()

    def guardar_estilos(self, nuevos_estilos: Dict[str, Any]) -> bool:
        """
        Persiste los nuevos estilos en artist.json y notifica al orquestador
        central para que actualice la apariencia en tiempo de ejecución.

        Args:
            nuevos_estilos: Diccionario con los valores de apariencia a guardar.

        Returns:
            True si la operación fue exitosa.
        """
        exito = self._modelo_artista.guardar_estilos(nuevos_estilos)

        if exito:
            # Notificar al MainController: actualiza los estilos activos en memoria
            # y reaplica set_appearance_mode / set_default_color_theme a CTk.
            self._controlador_principal.actualizar_estilos(nuevos_estilos)

        return exito