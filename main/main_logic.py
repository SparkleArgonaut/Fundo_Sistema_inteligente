import sys
import os
import sqlite3

# --- BLOQUE DE RUTA DINÁMICA ---
# no se muy bien que pasa acá pero sin esto no jala
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
# ------------------------------

#buscar en la carpeta ia la funcion de roya
try:
    from ia.coffee_processor import diagnosticar_roya
    print("modulo de ia cargado")
except ImportError as e:
    print(f"no aparece la carpeta 'ia' en {BASE_DIR}")
    sys.exit(1)



def ejecutar_ciclo_control():
   
    ruta_foto = os.path.join(BASE_DIR, "data", "fotos", "captura_actual.jpg")
    ruta_db = os.path.join(BASE_DIR, "data", "DB_database.db")

    try:
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        
        print("consultando sensores...")
        print("analizando imagen del cultivo...")
        
        
        resultado, confianza = diagnosticar_roya(ruta_foto)
        print(f"sincronizando: {resultado} ({confianza:.2%})")

        
        cursor.execute("""
            INSERT INTO analisis_vision (id_lectura, resultado_ia, confianza_ia, ruta_imagen) 
            VALUES (?, ?, ?, ?)
        """, (1, resultado, confianza, ruta_foto))
        
        conn.commit()
        print("correcto: se guarda registro con respaldo")

    except Exception as e:
        print(f"ERROR en: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    ejecutar_ciclo_control()