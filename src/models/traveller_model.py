import json
import os

class ModeloViajero:
    def __init__(self):
        self.directorio_base = "basement"
        self.ruta_archivo = os.path.join(self.directorio_base, "traveller.json")
        self._asegurar_directorio()

    def _asegurar_directorio(self):
        if not os.path.exists(self.directorio_base):
            os.makedirs(self.directorio_base, exist_ok=True)

    def leer_rutas(self) -> dict:
        if not os.path.exists(self.ruta_archivo):
            return {"ruta_descarga": "", "ruta_picard": "", "ruta_cookies": ""}
            
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return {"ruta_descarga": "", "ruta_picard": "", "ruta_cookies": ""}

    def guardar_rutas(self, rutas: dict):
        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(rutas, archivo, indent=4)