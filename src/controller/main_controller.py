from src.view.davinci_view import DavinciView
from src.view.utils_view import UtilsView

class ControladorPrincipal:
    def __init__(self, vista_principal, modelo_artista, modelo_viajero, servicio_descarga, servicio_picad):
        self.vista_principal = vista_principal
        self.modelo_artista = modelo_artista
        self.modelo_viajero = modelo_viajero
        
        from .style_controller import ControladorEstilo
        from .config_controller import ControladorConfig
        from .download_controller import ControladorDescarga
        from .picad_controller import ControladorPicad

        self.controlador_estilo = ControladorEstilo(self, self.modelo_artista)
        self.controlador_config = ControladorConfig(self.modelo_viajero)
        self.controlador_descarga = ControladorDescarga(servicio_descarga, self.modelo_viajero)
        self.controlador_picad = ControladorPicad(servicio_picad, self.modelo_viajero)

        self.controlador_descarga.establecer_controlador_picard(self.controlador_picad)
        self.tipo_vista_actual = "moderno"
        
        self.vista_principal.vincular_alternar_vista(self.alternar_vista)
        self.vista_principal.vincular_abrir_artist(self.abrir_configuracion_estilos)
        self.vista_principal.vincular_abrir_traveller(self.abrir_configuracion_rutas)
        self.vista_principal.vincular_abrir_picard(self.controlador_picad.abrir_picard)

        self.aplicar_estilo_global()
        self.renderizar_vista_activa()

        rutas = self.modelo_viajero.leer_rutas()
        if not rutas.get("ruta_descarga", "").strip():
            self.abrir_configuracion_rutas()

    def aplicar_estilo_global(self):
        estilos = self.modelo_artista.leer_estilos()
        tema = estilos.get("tema", "Windows Classic")
        self.vista_principal.inyectar_estilos(tema)

    def renderizar_vista_activa(self):
        vista_hija = self.vista_principal.renderizar_vista(self.tipo_vista_actual)
        self.controlador_descarga.establecer_vista_activa(vista_hija)

    def alternar_vista(self):
        # 1. SALVAMOS ESTADO ANTES DE DESTRUIR LA VISTA (Previene el TclError)
        self.controlador_descarga.guardar_estado_actual()

        # 2. Alternamos el identificador
        self.tipo_vista_actual = "tradicional" if self.tipo_vista_actual == "moderno" else "moderno"
        
        # 3. Renderizamos
        self.renderizar_vista_activa()

    def abrir_configuracion_estilos(self):
        vista_davinci = DavinciView(self.vista_principal)
        self.controlador_estilo.establecer_vista(vista_davinci)

    def abrir_configuracion_rutas(self):
        vista_utils = UtilsView(self.vista_principal)
        self.controlador_config.establecer_vista(vista_utils)