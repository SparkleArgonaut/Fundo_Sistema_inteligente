import tensorflow as tf
import numpy as np
from PIL import Image
import os
import sqlite3
import cv2

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "DB_database.db")
MODEL_DIR = os.path.join(BASE_DIR, "ia", "models")

MODEL_FILES = {
    "Roya":  "binrust.h5",
    "Phoma": "binphoma.h5"
    # Minador excluido: modelo roto, se detecta por color
}

# --- CARGA DE MODELOS ---
modelos = {}
for nombre, archivo in MODEL_FILES.items():
    path = os.path.join(MODEL_DIR, archivo)
    if os.path.exists(path):
        modelo = tf.keras.models.load_model(path, compile=False)
        print(f"[{nombre}] cargado | Input shape: {modelo.input_shape}")
        modelos[nombre] = modelo
    else:
        print(f"ADVERTENCIA: No se encontró {archivo}")


def detectar_minador_por_color(ruta_foto):
    """
    El minador deja manchas amarillas/cafés en la hoja.
    Detección por rango de color HSV, sin modelo.
    """
    img = cv2.imread(ruta_foto)
    if img is None:
        return False, 0.0

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Rango amarillo-café (manchas típicas de minador)
    lower = np.array([15, 40, 40])
    upper = np.array([35, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)
    porcentaje = np.sum(mask > 0) / mask.size

    print(f"DEBUG [Minador color]: {porcentaje:.4f} ({porcentaje*100:.1f}% píxeles afectados)")

    detectado = porcentaje > 0.15  # subimos de 8% a 15%
    return detectado, float(porcentaje)


def preprocesar_imagen(ruta_foto, target_size):
    img_cv2 = cv2.imread(ruta_foto)
    if img_cv2 is None:
        raise ValueError(f"No se pudo leer: {ruta_foto}")

    # CLAHE para reducir reflejos
    lab = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_edit = clahe.apply(l)
    final_lab = cv2.merge((l_edit, a, b))
    img_rgb = cv2.cvtColor(final_lab, cv2.COLOR_LAB2RGB)

    img_pil = Image.fromarray(img_rgb).resize(target_size, Image.LANCZOS)
    img_array = np.array(img_pil).astype(np.float32) / 255.0
    return np.expand_dims(img_array, axis=0)


def obtener_probabilidad(modelo, img_array):
    salida_raw = modelo.predict(img_array, verbose=0)[0][0]
    ultima_activacion = getattr(modelo.layers[-1], 'activation', None)

    tiene_sigmoid = (
        ultima_activacion is not None and
        hasattr(ultima_activacion, '__name__') and
        'sigmoid' in ultima_activacion.__name__
    )

    if tiene_sigmoid:
        return float(salida_raw)
    else:
        return float(1 / (1 + np.exp(-salida_raw)))


def procesar_y_guardar_diagnostico(ruta_foto):
    if not os.path.exists(ruta_foto):
        print(f"Error: No se encuentra la imagen en {ruta_foto}")
        return

    reporte_detecciones = []

    # --- 1. MODELOS IA (Roya y Phoma) ---
    for nombre, modelo in modelos.items():
        h, w = modelo.input_shape[1], modelo.input_shape[2]
        img_array = preprocesar_imagen(ruta_foto, (w, h))
        prob = obtener_probabilidad(modelo, img_array)
        print(f"DEBUG [{nombre}]: {prob:.4f}")

        if prob > 0.50:
            reporte_detecciones.append((nombre, prob))

    # --- 2. MINADOR POR COLOR ---
    minador_detectado, confianza_minador = detectar_minador_por_color(ruta_foto)
    if minador_detectado:
        reporte_detecciones.append(("Minador", confianza_minador))

    # --- 3. RESULTADO FINAL ---
    if reporte_detecciones:
        nombres = ", ".join([n for n, _ in reporte_detecciones])
        confianza_final = max([c for _, c in reporte_detecciones])
        resultado_final = nombres
    else:
        resultado_final = "Café Sano"
        confianza_final = 0.99

    print(f"\nRESULTADO: {resultado_final} (confianza: {confianza_final:.4f})")

    # --- 4. GUARDAR EN DB ---
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analisis_vision (id_lectura, resultado_ia, confianza_ia, ruta_imagen)
            VALUES (?, ?, ?, ?)
        """, (1, resultado_final, float(confianza_final), ruta_foto))
        conn.commit()
        conn.close()
        print("Guardado en DB OK")
    except Exception as e:
        print(f"Error BD: {e}")