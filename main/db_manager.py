import sqlite3
import os

# Configuración de rutas relativas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "DB_database.db")

def registrar_ia(id_lectura, ruta_foto, resultado, confianza):
   
   # id_lectura: ID proveniente de la tabla lecturas_sensores
  
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
       
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
    test_id = registrar_ia(None, "data/fotos/limpieza_test.jpg", "Sistema OK", 1.0)
    if test_id:
        print(f"registro de prueba creado con ID: {test_id}")
    else:
        print("ERROR en el test. 'DB_database.db' no esta en /data")