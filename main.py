from src.view.main_view import MainView

from src.models.artist_model import ModeloArtista
from src.models.traveller_model import ModeloViajero

from src.services.download_service import ServicioDescarga
from src.services.picad_service import ServicioPicad

from src.controller.main_controller import ControladorPrincipal

def iniciar_aplicacion():
    modelo_artista = ModeloArtista()
    modelo_viajero = ModeloViajero()

    servicio_descarga = ServicioDescarga()
    servicio_picad = ServicioPicad()

    vista_principal = MainView()

    _controlador = ControladorPrincipal(
        vista_principal=vista_principal,
        modelo_artista=modelo_artista,
        modelo_viajero=modelo_viajero,
        servicio_descarga=servicio_descarga,
        servicio_picad=servicio_picad
    )

    vista_principal.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()