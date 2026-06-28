class ControladorEstilo:
    def __init__(self, controlador_principal, modelo_artista):
        self.controlador_principal = controlador_principal
        self.modelo_artista = modelo_artista
        self.vista_davinci = None

    def establecer_vista(self, vista):
        self.vista_davinci = vista
        
        # Cargar los datos actuales en la interfaz
        estilos_actuales = self.modelo_artista.leer_estilos()
        modo = estilos_actuales.get("modo_apariencia", "Dark")
        color = estilos_actuales.get("color_acento", "blue")
        
        self.vista_davinci.cargar_estilos(modo, color)
        self.vista_davinci.vincular_guardado(self.guardar_y_aplicar)

    def guardar_y_aplicar(self):
        nuevos_estilos = self.vista_davinci.obtener_estilos()
        
        # Persistir en JSON
        self.modelo_artista.guardar_estilos(nuevos_estilos)
        
        # Aplicar los cambios en tiempo real a toda la app
        self.controlador_principal.aplicar_estilo_global()
        
        # Cerrar la ventana emergente
        self.vista_davinci.destroy()