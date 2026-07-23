import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "data", "DB_database.db")

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

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
    CREATE TABLE IF NOT EXISTS lecturas_sensor (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora   TIMESTAMP DEFAULT (datetime('now','localtime')),
        estado_suelo TEXT,
        valor_raw    INTEGER
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS registro_gestion (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora   TIMESTAMP DEFAULT (datetime('now','localtime')),
        tipo_alerta  TEXT,
        mensaje      TEXT,
        estado_accion TEXT DEFAULT 'Pendiente'
    )
""")

conn.commit()
conn.close()
print("DB inicializada OK")