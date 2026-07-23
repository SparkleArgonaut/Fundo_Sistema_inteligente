from flask import Flask, jsonify
import sqlite3
import os
from flask_cors import CORS







app = Flask(__name__)
CORS(app) 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "data", "DB_database.db")


def query_db(sql, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, args)
    rv = cur.fetchall()
    conn.close()
    return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]


@app.route("/api/inicio")
def inicio():
    ultimo_analisis = query_db("""
        SELECT resultado_ia, confianza_ia, fecha_hora, ruta_imagen
        FROM analisis_vision
        ORDER BY id_analisis DESC LIMIT 1
    """, one=True)

    ultimo_sensor = query_db("""
        SELECT estado_suelo, fecha_hora
        FROM lecturas_sensor
        ORDER BY id DESC LIMIT 1
    """, one=True)

    return jsonify({
        "ultimo_analisis": ultimo_analisis,
        "ultimo_sensor":   ultimo_sensor
    })


@app.route("/api/registros")
def registros():
    datos = query_db("""
        SELECT id_analisis, resultado_ia, confianza_ia, fecha_hora
        FROM analisis_vision
        ORDER BY id_analisis DESC
        LIMIT 20
    """)
    return jsonify(datos)


@app.route("/api/notificaciones")
def notificaciones():
    alertas = query_db("""
        SELECT id, tipo_alerta, mensaje, fecha_hora, estado_accion
        FROM registro_gestion
        ORDER BY id DESC
        LIMIT 20
    """)
    return jsonify(alertas)


@app.route("/api/lotes")
def lotes():
    analisis = query_db("""
        SELECT resultado_ia, confianza_ia, fecha_hora
        FROM analisis_vision
        ORDER BY id_analisis DESC LIMIT 1
    """, one=True)

    sensor = query_db("""
        SELECT estado_suelo
        FROM lecturas_sensor
        ORDER BY id DESC LIMIT 1
    """, one=True)

    estado = "Saludable"
    if analisis and analisis["resultado_ia"] != "Café Sano":
        estado = "Alarma"
    elif sensor and sensor["estado_suelo"] == "Seco":
        estado = "Alerta"

    return jsonify([{
        "nombre":             "Lote 1",
        "estado":             estado,
        "humedad":            sensor["estado_suelo"] if sensor else "Desconocido",
        "ultimo_diagnostico": analisis["resultado_ia"] if analisis else "Sin datos"
    }])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)