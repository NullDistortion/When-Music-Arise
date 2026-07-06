import os
import sys

def obtener_ruta_absoluta(ruta_relativa: str) -> str:
    if getattr(sys, 'frozen', False):
        directorio_base = sys._MEIPASS
    else:
        directorio_base = os.path.abspath(".")
        
    return os.path.join(directorio_base, ruta_relativa)