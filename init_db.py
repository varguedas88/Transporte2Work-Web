import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
DROP TABLE IF EXISTS usuarios;
""")

cur.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identificacion TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    primer_apellido TEXT NOT NULL,
    segundo_apellido TEXT,
    correo TEXT UNIQUE NOT NULL,
    telefono TEXT NOT NULL,
    contrasena TEXT NOT NULL,
    rol TEXT DEFAULT 'usuario'
);
""")

conn.commit()
conn.close()

print("✔ Base de datos recreada correctamente.")

