import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# --- Tabla usuarios ---
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT,
    rol TEXT,
    contrasena TEXT
);
""")

# --- Tabla choferes ---
cur.execute("""
CREATE TABLE IF NOT EXISTS choferes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    telefono TEXT,
    cedula TEXT,
    licencia_tipo TEXT,
    fecha_contratacion TEXT
);
""")

# --- Tabla buses ---
cur.execute("""
CREATE TABLE IF NOT EXISTS buses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT,
    modelo TEXT,
    capacidad INTEGER,
    costo_km REAL,
    chofer_id INTEGER,
    FOREIGN KEY (chofer_id) REFERENCES choferes(id)
);
""")

# --- Tabla reservas ---
cur.execute("""
CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    bus_id INTEGER,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    estado TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (bus_id) REFERENCES buses(id)
);
""")

conn.commit()
conn.close()

print("✔ Base de datos recreada correctamente.")
