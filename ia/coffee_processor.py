import tensorflow as tf
import numpy as np
from PIL import Image
import os
import sqlite3
import cv2
import tf_keras as keras

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, "data", "DB_database.db")
MODEL_DIR = os.path.join(BASE_DIR, "ia", "models")

MODEL_FILES = {
    "Roya":    "binrust.h5",
    "Phoma":   "binphoma.h5",
}

modelos = {}
for nombre, archivo in MODEL_FILES.items():
    path = os.path.join(MODEL_DIR, archivo)
    if os.path.exists(path):
        modelo = keras.models.load_model(path, compile=False)
        print(f"[{nombre}] cargado | Input shape: {modelo.input_shape}")
        modelos[nombre] = modelo
    else:
        print(f"ADVERTENCIA: No se encontró {archivo}")


def detectar_minador_por_color(ruta_foto):
    img = cv2.imread(ruta_foto)
    if img is None:
        return False, 0.0

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([15, 40, 40])
    upper = np.array([35, 255, 255])
    mask  = cv2.inRange(hsv, lower, upper)

    porcentaje = np.sum(mask > 0) / mask.size
    print(f"DEBUG [Minador color]: {porcentaje*100:.1f}% píxeles afectados")

    return porcentaje > 0.25, float(porcentaje)


def preprocesar_imagen(ruta_foto, target_size):
    img_cv2 = cv2.imread(ruta_foto)
    if img_cv2 is None:
        raise ValueError(f"No se pudo leer: {ruta_foto}")

    # CLAHE en canal L
    lab    = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe  = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_edit = clahe.apply(l)
    img_procesada = cv2.merge((l_edit, a, b))
    img_procesada = cv2.cvtColor(img_procesada, cv2.COLOR_LAB2BGR)

    img_pil   = Image.fromarray(img_procesada)
    img_pil   = img_pil.resize(target_size, Image.LANCZOS)
    img_array = np.array(img_pil).astype(np.float32)  
    return np.expand_dims(img_array, axis=0)


def obtener_probabilidad(modelo, img_array):
    salida_raw = modelo.predict(img_array, verbose=0)[0][0]
    activacion = getattr(modelo.layers[-1], 'activation', None)
    tiene_sigmoid = (
        activacion is not None and
        hasattr(activacion, '__name__') and
        'sigmoid' in activacion.__name__
    )
    if tiene_sigmoid:
        return float(salida_raw)
    return float(1 / (1 + np.exp(-salida_raw)))


def procesar_y_guardar_diagnostico(ruta_foto):
    if not os.path.exists(ruta_foto):
        print(f"Error: No se encuentra la imagen en {ruta_foto}")
        return

    reporte_detecciones = []

    # 1. Modelos IA
    for nombre, modelo in modelos.items():
        h, w      = modelo.input_shape[1], modelo.input_shape[2]
        img_array = preprocesar_imagen(ruta_foto, (w, h))
        prob      = obtener_probabilidad(modelo, img_array)
        print(f"DEBUG [{nombre}]: {prob:.4f}")
        if prob > 0.50:
            reporte_detecciones.append((nombre, prob))

    # 2. Minador por color
    detectado, confianza_minador = detectar_minador_por_color(ruta_foto)
    if detectado:
        reporte_detecciones.append(("Minador", confianza_minador))

    # 3. Resultado final  
    if reporte_detecciones:
        resultado_final  = ", ".join([n for n, _ in reporte_detecciones])
        confianza_final  = max([c for _, c in reporte_detecciones])
    else:
        resultado_final  = "Café Sano"
        confianza_final  = 0.99

    print(f"\nRESULTADO: {resultado_final} (confianza: {confianza_final:.4f})")

    # --- 4. Guardar en DB ---
    try:
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analisis_vision (
                id_analisis  INTEGER PRIMARY KEY AUTOINCREMENT,
                id_lectura   INTEGER,
                fecha_hora   TIMESTAMP DEFAULT (datetime('now','localtime')),
                ruta_imagen  TEXT,
                resultado_ia TEXT,
                confianza_ia REAL
            )
        """)
        cursor.execute("""
            INSERT INTO analisis_vision (id_lectura, ruta_imagen, resultado_ia, confianza_ia)
            VALUES (?, ?, ?, ?)
        """, (1, ruta_foto, resultado_final, float(confianza_final)))
        conn.commit()
        conn.close()
        print("Guardado en DB OK")
    except Exception as e:
        print(f"Error BD: {e}")

    return resultado_final  # ← al final de todo