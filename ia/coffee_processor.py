import numpy as np
from PIL import Image
import os
import sqlite3
import cv2

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, "data", "DB_database.db")
MODEL_DIR = os.path.join(BASE_DIR, "ia", "models")

# ─────────────────────────────────────────
# CARGA DE MODELOS — TFLite en Pi, TF en PC
# ─────────────────────────────────────────
USAR_TFLITE = os.path.exists(os.path.join(MODEL_DIR, "binrust.tflite"))

modelos = {}

if USAR_TFLITE:
    print("[IA] Modo TFLite (Raspberry Pi)")
    try:
        import tflite_runtime.interpreter as tflite
    except ImportError:
        import tensorflow.lite as tflite

    TFLITE_FILES = {
        "Roya":  "binrust.tflite",
        "Phoma": "binphoma.tflite"
    }
    for nombre, archivo in TFLITE_FILES.items():
        path = os.path.join(MODEL_DIR, archivo)
        if os.path.exists(path):
            interp = tflite.Interpreter(model_path=path)
            interp.allocate_tensors()
            modelos[nombre] = interp
            print(f"[{nombre}] TFLite cargado")
        else:
            print(f"ADVERTENCIA: No se encontró {archivo}")

else:
    print("[IA] Modo TensorFlow completo (PC)")
    os.environ['TF_USE_LEGACY_KERAS'] = '1'
    import tensorflow as tf

    H5_FILES = {
        "Roya":    "binrust.h5",
        "Phoma":   "binphoma.h5",
        "Minador": "binminer.h5"
    }
    for nombre, archivo in H5_FILES.items():
        path = os.path.join(MODEL_DIR, archivo)
        if os.path.exists(path):
            modelo = tf.keras.models.load_model(path, compile=False)
            print(f"[{nombre}] TF cargado | Input shape: {modelo.input_shape}")
            modelos[nombre] = modelo
        else:
            print(f"ADVERTENCIA: No se encontró {archivo}")


# ─────────────────────────────────────────
# PREPROCESAMIENTO
# ─────────────────────────────────────────
def preprocesar_imagen(ruta_foto, target_size):
    img_cv2 = cv2.imread(ruta_foto)
    if img_cv2 is None:
        raise ValueError(f"No se pudo leer: {ruta_foto}")

    lab     = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe   = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_edit  = clahe.apply(l)
    img_procesada = cv2.cvtColor(cv2.merge((l_edit, a, b)), cv2.COLOR_LAB2BGR)

    img_pil   = Image.fromarray(img_procesada).resize(target_size, Image.LANCZOS)
    img_array = np.array(img_pil).astype(np.float32)  # 0-255 sin normalizar
    return np.expand_dims(img_array, axis=0)


# ─────────────────────────────────────────
# INFERENCIA — maneja TFLite y TF
# ─────────────────────────────────────────
def obtener_probabilidad(modelo, img_array):
    if USAR_TFLITE:
        input_details  = modelo.get_input_details()
        output_details = modelo.get_output_details()
        modelo.set_tensor(input_details[0]['index'], img_array)
        modelo.invoke()
        salida_raw = modelo.get_tensor(output_details[0]['index'])[0][0]
    else:
        salida_raw = modelo.predict(img_array, verbose=0)[0][0]

    # Sigmoid manual (modelos tienen activación linear)
    return float(1 / (1 + np.exp(-salida_raw)))


def obtener_input_size(modelo):
    if USAR_TFLITE:
        input_details = modelo.get_input_details()
        shape = input_details[0]['shape']  # [1, H, W, 3]
        return shape[2], shape[1]          # (W, H)
    else:
        return modelo.input_shape[2], modelo.input_shape[1]


# ─────────────────────────────────────────
# DETECCIÓN MINADOR POR COLOR
# ─────────────────────────────────────────
def detectar_minador_por_color(ruta_foto):
    img = cv2.imread(ruta_foto)
    if img is None:
        return False, 0.0

    hsv  = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([15, 40, 40]), np.array([35, 255, 255]))
    porcentaje = np.sum(mask > 0) / mask.size
    print(f"DEBUG [Minador color]: {porcentaje*100:.1f}% píxeles afectados")
    return porcentaje > 0.25, float(porcentaje)


# ─────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────
def procesar_y_guardar_diagnostico(ruta_foto):
    if not os.path.exists(ruta_foto):
        print(f"Error: No se encuentra la imagen en {ruta_foto}")
        return None

    reporte_detecciones = []

    # 1. Modelos IA
    for nombre, modelo in modelos.items():
        w, h      = obtener_input_size(modelo)
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
        resultado_final = ", ".join([n for n, _ in reporte_detecciones])
        confianza_final = max([c for _, c in reporte_detecciones])
    else:
        resultado_final = "Café Sano"
        confianza_final = 0.99

    print(f"\nRESULTADO: {resultado_final} (confianza: {confianza_final:.4f})")

    # 4. Guardar en DB
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

    return resultado_final