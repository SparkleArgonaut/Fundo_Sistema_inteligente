import os
import sys

# Rutas
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from ia.coffee_processor import procesar_y_guardar_diagnostico

def ejecutar_sistema():
    carpeta_fotos = os.path.join(ruta_raiz, "data", "fotos")
    
    # Obtener la imagen más reciente
    imagenes = [
        os.path.join(carpeta_fotos, f) 
        for f in os.listdir(carpeta_fotos) 
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    
    if not imagenes:
        print("ERROR: No hay imágenes en la carpeta")
        return
    
    ruta_imagen = max(imagenes, key=os.path.getmtime)
    print(f"\n--- SISTEMA FUNDO BERLÍN ---")
    print(f"Imagen detectada: {os.path.basename(ruta_imagen)}")
    
    procesar_y_guardar_diagnostico(ruta_imagen)



if __name__ == "__main__":
    ejecutar_sistema()