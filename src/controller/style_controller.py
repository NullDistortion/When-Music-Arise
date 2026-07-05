class ControladorEstilo:
    def __init__(self, controlador_principal, modelo_artista):
        self.controlador_principal = controlador_principal
        self.modelo_artista = modelo_artista
        self.vista_davinci = None

    def establecer_vista(self, vista):
        self.vista_davinci = vista
        
        estilos_actuales = self.modelo_artista.leer_estilos()
        tema = estilos_actuales.get("tema", "Windows Classic")
        
        self.vista_davinci.cargar_estilos(tema)
        self.vista_davinci.vincular_guardado(self.guardar_y_aplicar)

    def guardar_y_aplicar(self):
        nuevos_estilos = self.vista_davinci.obtener_estilos()
        self.modelo_artista.guardar_estilos(nuevos_estilos)
        self.controlador_principal.aplicar_estilo_global()
        self.vista_davinci.destroy()