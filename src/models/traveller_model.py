import json
import os

class ModeloViajero:
    """Gestiona la persistencia de las rutas locales del usuario."""
    
    def __init__(self):
        self.directorio_base = "basement"
        self.ruta_archivo = os.path.join(self.directorio_base, "traveller.json")
        self._asegurar_directorio()

    def _asegurar_directorio(self):
        if not os.path.exists(self.directorio_base):
            os.makedirs(self.directorio_base, exist_ok=True)

    def leer_rutas(self) -> dict:
        """Retorna las rutas guardadas o cadenas vacías por defecto."""
        if not os.path.exists(self.ruta_archivo):
            return {"ruta_descarga": "", "ruta_picard": ""}
            
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return {"ruta_descarga": "", "ruta_picard": ""}

    def guardar_rutas(self, rutas: dict):
        """Sobrescribe el archivo JSON con las nuevas rutas de destino."""
        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(rutas, archivo, indent=4)