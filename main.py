import sys
import sqlite3
import schedule
import time
import cv2
import numpy as np
from datetime import datetime
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOTOS_DIR = os.path.join(BASE_DIR, "data", "fotos")
DB_PATH   = os.path.join(BASE_DIR, "data", "DB_database.db")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ia.coffee_processor import procesar_y_guardar_diagnostico

os.makedirs(FOTOS_DIR, exist_ok=True)



# 1. CÁMARA


def tomar_foto():
    nombre = f"cafe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    ruta   = os.path.join(FOTOS_DIR, nombre)

    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.start()
        cam.capture_file(ruta)
        cam.stop()
        print(f"[Camara Pi] {nombre}")
        return ruta

    except ImportError:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            ret, frame = cam.read()
            cam.release()
            if ret:
                cv2.imwrite(ruta, frame)
                print(f"[webcam] {nombre}")
                return ruta

        # sin camara disponible -> usar última foto existente
        imagenes = [
            os.path.join(FOTOS_DIR, f)
            for f in os.listdir(FOTOS_DIR)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if imagenes:
            ultima = max(imagenes, key=os.path.getmtime)
            print(f"[sin camara] usando ultima foto: {os.path.basename(ultima)}")
            return ultima
        
        print("ERROR: No hay camara ni fotos disponibles")
        return None


# ─────────────────────────────────────────
# 2. SENSOR DE SUELO
# ─────────────────────────────────────────
def leer_sensor():
    try:
        import RPi.GPIO as GPIO
        PIN = 11
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.IN)
        valor  = GPIO.input(PIN)
        GPIO.cleanup()
        estado = "Seco" if valor == 1 else "Humedo"
        print(f"[Sensor] {estado} (señal: {valor})")

    except ImportError:
        import random
        valor  = random.choice([0, 1])
        estado = "Seco" if valor == 1 else "Humedo"
        print(f"[Sensor simulado] {estado} (señal: {valor})")

    try:
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lecturas_sensor (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora  TIMESTAMP DEFAULT (datetime('now','localtime')),
                estado_suelo TEXT,
                valor_raw   INTEGER
            )
        """)
        cursor.execute(
            "INSERT INTO lecturas_sensor (estado_suelo, valor_raw) VALUES (?, ?)",
            (estado, valor)
        )
        conn.commit()
        conn.close()
        print("[Sensor] Guardado en DB OK")
    except Exception as e:
        print(f"Error BD sensor: {e}")

    return estado, valor


def registrar_alerta(tipo, mensaje):
    try:
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registro_gestion (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora    TIMESTAMP DEFAULT (datetime('now','localtime')),
                tipo_alerta   TEXT,
                mensaje       TEXT,
                estado_accion TEXT DEFAULT 'Pendiente'
            )
        """)
        cursor.execute("""
            INSERT INTO registro_gestion (tipo_alerta, mensaje)
            VALUES (?, ?)
        """, (tipo, mensaje))
        conn.commit()
        conn.close()
        print(f"[Alerta] {tipo}: {mensaje}")
    except Exception as e:
        print(f"Error BD alerta: {e}")


def ciclo_completo():
    print("\n" + "="*40)
    print(f"  CICLO  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*40)

    # 1. Sensor
    estado, valor = leer_sensor()
    if estado == "Seco":
        registrar_alerta("Estrés Hídrico", "Suelo seco detectado en Lote 1")

    # 2. Foto
    ruta_foto = tomar_foto()

    # 3. IA
    if ruta_foto:
        from ia.coffee_processor import procesar_y_guardar_diagnostico
        resultado = procesar_y_guardar_diagnostico(ruta_foto)
        if resultado and resultado != "Café Sano":
            registrar_alerta("Plaga/Enfermedad", f"{resultado} detectado en Lote 1")
    else:
        print("AVISO: Sin foto, se omite análisis IA")

    print("="*40 + "\n")



# 4. TEMPORIZADOR

schedule.every().day.at("09:00").do(ciclo_completo)
schedule.every().day.at("15:00").do(ciclo_completo)

if __name__ == "__main__":
    print("Sistema Fundo Berlin activo")
    print("Capturas programadas: 09:00 y 15:00")
    print("Presiona Ctrl+C para detener\n")

    
    ciclo_completo()

    while True:
        schedule.run_pending()
        time.sleep(30)