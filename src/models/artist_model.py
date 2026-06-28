import json
import os

class ModeloArtista:
    """Gestiona la persistencia de los estilos visuales (Tema y Color)."""
    
    def __init__(self):
        # Aseguramos que la ruta apunte a la carpeta basement en la raíz del proyecto
        self.directorio_base = "basement"
        self.ruta_archivo = os.path.join(self.directorio_base, "artist.json")
        self._asegurar_directorio()

    def _asegurar_directorio(self):
        if not os.path.exists(self.directorio_base):
            os.makedirs(self.directorio_base, exist_ok=True)

    def leer_estilos(self) -> dict:
        """Retorna los estilos guardados o los valores por defecto si falla/no existe."""
        if not os.path.exists(self.ruta_archivo):
            return {"modo_apariencia": "Dark", "color_acento": "blue"}
            
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return {"modo_apariencia": "Dark", "color_acento": "blue"}

    def guardar_estilos(self, estilos: dict):
        """Sobrescribe el archivo JSON con la nueva configuración visual."""
        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(estilos, archivo, indent=4)