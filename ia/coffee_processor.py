import tensorflow as tf
import numpy as np
from PIL import Image
import os

# forzamos a keras a usar el formato cargador 
MODEL_PATH = os.path.join("ia", "models", "binrust.h5")

# cargar sin compilar
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print("este mensaje significa que keras funciona")

def diagnosticar_roya(ruta_imagen):
    img = Image.open(ruta_imagen).resize((1024, 1024)) 
    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 1. Obtener el valor crudo (Logit)
    logit = model.predict(img_array, verbose=0)[0][0]

    # 2. Aplicar función Sigmoide manual para normalizar a 0-1
    # formula: 1 / (1 + exp(-x))
    probabilidad = 1 / (1 + np.exp(-logit))

    # 3. Lógica de decisión
    if probabilidad > 0.5:
        resultado = "Roya Detectada"
        confianza = probabilidad
    else:
        resultado = "Café Sano"
        confianza = 1 - probabilidad
    
    return resultado, confianza

if __name__ == "__main__":
    foto = os.path.join("data", "fotos", "test_ia.jpg")
    if os.path.exists(foto):
        res, conf = diagnosticar_roya(foto)
        print(f"\n DIAGNOSTICO: {res} | Certeza: {conf:.2%}")
    else:
        print(f"no existe la foto en: {foto}")