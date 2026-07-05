import json
import os

class ModeloArtista:
    def __init__(self):
        self.directorio_base = "basement"
        self.ruta_archivo = os.path.join(self.directorio_base, "artist.json")
        self._asegurar_directorio()

    def _asegurar_directorio(self):
        if not os.path.exists(self.directorio_base):
            os.makedirs(self.directorio_base, exist_ok=True)

    def leer_estilos(self) -> dict:
        if not os.path.exists(self.ruta_archivo):
            return {"tema": "Windows Classic"}
            
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return {"tema": "Windows Classic"}

    def guardar_estilos(self, estilos: dict):
        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(estilos, archivo, indent=4)