import os
import sys

# Rutas
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from ia.coffee_processor import procesar_y_guardar_diagnostico

def ejecutar_sistema():
    ruta_imagen = os.path.join(ruta_raiz, "data", "fotos", "test_ia.jpg")

    print("\n--- SISTEMA FUNDO BERLÍN ---")

    if not os.path.exists(ruta_imagen):
        print(f"ERROR: Imagen no encontrada en: {ruta_imagen}")
        return

    procesar_y_guardar_diagnostico(ruta_imagen)

if __name__ == "__main__":
    ejecutar_sistema()