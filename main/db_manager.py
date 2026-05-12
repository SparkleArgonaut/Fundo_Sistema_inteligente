import sqlite3
import os

# Configuración de rutas relativas (Subiendo un nivel desde /ia o /database)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "DB_database.db")

def registrar_ia(id_lectura, ruta_foto, resultado, confianza):
    """
    Función de registro para los resultados de Visión Artificial.
    Adaptada para coincidir con tu lógica de 'id_lectura' y 'fecha_hora'.
    """
    try:
        # Asegurarse de que el directorio data existe
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Creamos la tabla si no existe (con tus nombres exactos de columnas)
        cursor.execute('''CREATE TABLE IF NOT EXISTS analisis_vision 
                          (id_analisis INTEGER PRIMARY KEY AUTOINCREMENT,
                           id_lectura INTEGER, 
                           fecha_hora TIMESTAMP, 
                           ruta_imagen TEXT, 
                           resultado_ia TEXT, 
                           confianza_ia REAL)''')

        # Insertamos usando datetime('now', 'localtime') como en tu código original
        query = '''INSERT INTO analisis_vision 
                   (id_lectura, fecha_hora, ruta_imagen, resultado_ia, confianza_ia) 
                   VALUES (?, datetime('now', 'localtime'), ?, ?, ?)'''
        
        cursor.execute(query, (id_lectura, ruta_foto, resultado, confianza))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    except sqlite3.Error as e:
        print(f"ERROR de SQLITE: {e}")
        return None
    except Exception as e:
        print(f"ERROR en BD: {e}")
        return None

if __name__ == "__main__":
    print("--- Test de Limpieza: db_manager.py ---")
    # Probamos con un ID nulo para verificar consistencia
    test_id = registrar_ia(None, "data/fotos/limpieza_test.jpg", "Sistema OK", 1.0)
    if test_id:
        print(f"Registro de prueba creado con ID: {test_id}")
    else:
        print("ERROR: No se pudo crear el registro. Revisa la ruta de 'data/'")