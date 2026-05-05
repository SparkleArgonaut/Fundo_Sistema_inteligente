CREATE TABLE IF NOT EXISTS lecturas_sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    humedad_suelo REAL NOT NULL,
    temperatura_ambiente REAL,
    id_dispositivo TEXT
);


CREATE TABLE IF NOT EXISTS analisis_vision (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ruta_imagen TEXT NOT NULL,        
    resultado_ia TEXT NOT NULL,       
    confianza_ia REAL,               
    FOREIGN KEY (id) REFERENCES lecturas_sensores(id)
);


CREATE TABLE IF NOT EXISTS registro_gestion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_alerta TEXT,                
    mensaje TEXT,                     
    estado_accion TEXT DEFAULT 'Pendiente' 
);