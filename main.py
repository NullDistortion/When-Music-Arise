from src.view.main_view import MainView

from src.models.artist_model import ModeloArtista
from src.models.traveller_model import ModeloViajero

from src.services.download_service import ServicioDescarga
from src.services.picad_service import ServicioPicad

from src.controller.main_controller import ControladorPrincipal

def iniciar_aplicacion():
    # 1. Instanciar los Modelos (Base de datos JSON)
    modelo_artista = ModeloArtista()
    modelo_viajero = ModeloViajero()

    # 2. Instanciar los Servicios (Procesos en segundo plano)
    servicio_descarga = ServicioDescarga()
    servicio_picad = ServicioPicad()

    # 3. Instanciar la Vista Principal (Contenedor GUI)
    vista_principal = MainView()

    # 4. Inyectar todo al Controlador Principal (El cerebro que orquesta)
    # Se guarda en una variable para evitar que el recolector de basura de Python lo elimine
    _controlador = ControladorPrincipal(
        vista_principal=vista_principal,
        modelo_artista=modelo_artista,
        modelo_viajero=modelo_viajero,
        servicio_descarga=servicio_descarga,
        servicio_picad=servicio_picad
    )

    # 5. Arrancar el bucle gráfico
    vista_principal.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()