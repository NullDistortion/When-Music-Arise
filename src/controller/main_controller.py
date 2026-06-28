"""
main_controller.py
------------------
Orquestador central de "When Music Arise".
Responsabilidades:
  · Mantener el estilo visual activo en memoria durante toda la sesión.
  · Aplicar el tema a customtkinter al iniciar y al recibir cambios.
  · Instanciar todos los sub-controladores y la vista raíz.
  · Exponer métodos de navegación (cambio de vista, apertura de ventanas).
  · Proveer acceso a los sub-controladores para el resto del sistema.
"""

import customtkinter as ctk
from typing import Any, Dict, Optional


class MainController:
    """
    Punto de control único que orquesta el flujo completo de la aplicación.
    Retiene los estilos activos en memoria e inyecta ese contexto cada vez
    que se produce un cambio de frame, según la especificación de la arquitectura.
    """

    def __init__(self) -> None:
        # Importación diferida para evitar dependencias circulares
        from src.models.artist_model import ArtistModel

        self._modelo_artista = ArtistModel()

        # Diccionario de sub-controladores (poblado en iniciar())
        self._controladores: Dict[str, Any] = {}

        # Referencia a la vista principal (MainView / CTk root window)
        self._vista_principal: Optional[Any] = None

        # ── Estilos activos en memoria ────────────────────────────────────────
        # Se carga una vez al arranque y se actualiza sin volver a leer el disco
        # cuando el usuario cambia la apariencia en tiempo de ejecución.
        self._estilos_activos: Dict[str, Any] = {}
        self._cargar_y_aplicar_estilos()

    # ── Arranque ──────────────────────────────────────────────────────────────

    def iniciar(self) -> None:
        """
        Crea la vista raíz, instancia todos los sub-controladores,
        los inyecta en la vista y arranca el mainloop de Tkinter.
        """
        from src.view.main_view import MainView
        from src.controller.download_controller import DownloadController
        from src.controller.picad_controller import PicadController
        from src.controller.style_controller import StyleController
        from src.controller.config_controller import ConfigController

        # ── Crear la ventana raíz ─────────────────────────────────────────────
        self._vista_principal = MainView(controlador_principal=self)

        # ── Instanciar sub-controladores ──────────────────────────────────────
        # Cada controlador recibe referencias mínimas: la vista raíz para
        # el paso de callbacks hilo-seguro, y este orquestador para
        # solicitar datos de otros controladores sin acoplamiento directo.
        self._controladores["descarga"] = DownloadController(
            vista=self._vista_principal,
            controlador_principal=self,
        )
        self._controladores["picard"] = PicadController(
            vista=self._vista_principal,
            controlador_principal=self,
        )
        self._controladores["estilo"] = StyleController(
            controlador_principal=self,
        )
        self._controladores["config"] = ConfigController(
            controlador_principal=self,
        )

        # ── Inyectar controladores en la vista raíz ───────────────────────────
        # Tras la inyección, main_view lanza el primer frame (vista moderna por defecto)
        self._vista_principal.inyectar_controladores(self._controladores)

        # ── Iniciar el mainloop de Tkinter/CustomTkinter ──────────────────────
        self._vista_principal.mainloop()

    # ── Gestión de estilos ────────────────────────────────────────────────────

    def _cargar_y_aplicar_estilos(self) -> None:
        """Lee los estilos desde artist.json y los aplica a customtkinter."""
        self._estilos_activos = self._modelo_artista.leer_estilos()
        self._aplicar_estilos_a_ctk(self._estilos_activos)

    def _aplicar_estilos_a_ctk(self, estilos: Dict[str, Any]) -> None:
        """
        Aplica el modo de apariencia y el tema de color a customtkinter.
        Ambas llamadas son globales y afectan a todos los widgets existentes.
        """
        modo_apariencia = estilos.get("modo_apariencia", "dark")
        tema_color      = estilos.get("tema_color", "green")

        ctk.set_appearance_mode(modo_apariencia)      # "dark" | "light" | "system"
        ctk.set_default_color_theme(tema_color)       # "blue" | "green" | "dark-blue"

    def actualizar_estilos(self, nuevos_estilos: Dict[str, Any]) -> None:
        """
        Actualiza los estilos activos en memoria y los reaplica a customtkinter.
        Llamado por StyleController tras guardar nuevos estilos.

        Args:
            nuevos_estilos: Diccionario parcial o completo con los nuevos valores.
        """
        self._estilos_activos.update(nuevos_estilos)
        self._aplicar_estilos_a_ctk(self._estilos_activos)

    def obtener_estilos_activos(self) -> Dict[str, Any]:
        """Retorna una copia defensiva de los estilos activos en memoria."""
        return self._estilos_activos.copy()

    # ── Navegación entre vistas ───────────────────────────────────────────────
    # Cada método inyecta los estilos activos al cambiar de frame,
    # preservando el contexto visual (FLUJO DE VISTAS ESTRICTO).

    def cambiar_a_vista_moderna(self) -> None:
        """Instruye a main_view para mostrar la vista moderna (barra de progreso)."""
        if self._vista_principal:
            # Se inyectan los estilos activos para que la nueva vista
            # utilice el color de acento y el modo correcto.
            self._vista_principal.mostrar_vista_moderna(self._estilos_activos)

    def cambiar_a_vista_tradicional(self) -> None:
        """Instruye a main_view para mostrar la vista tradicional (consola de texto)."""
        if self._vista_principal:
            self._vista_principal.mostrar_vista_tradicional(self._estilos_activos)

    # ── Apertura de ventanas auxiliares ──────────────────────────────────────

    def abrir_configuracion(self) -> None:
        """Abre la ventana de configuración de rutas (UtilsView / Traveller)."""
        controlador_config = self._controladores.get("config")
        if controlador_config:
            controlador_config.abrir_ventana_configuracion()

    def abrir_estilos(self) -> None:
        """Abre la ventana de personalización visual (DavinciView / Artist)."""
        controlador_estilo = self._controladores.get("estilo")
        if controlador_estilo:
            controlador_estilo.abrir_ventana_estilos()

    # ── Acceso a sub-controladores ────────────────────────────────────────────

    def obtener_controlador(self, nombre: str) -> Optional[Any]:
        """
        Retorna un sub-controlador por nombre.
        Permite que un controlador consulte a otro sin acoplamiento directo.

        Args:
            nombre: Clave del controlador ("descarga", "picard", "estilo", "config").

        Returns:
            La instancia del controlador o None si no existe.
        """
        return self._controladores.get(nombre)