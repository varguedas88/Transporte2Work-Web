import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Tabla usuarios
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE,
    rol TEXT DEFAULT 'usuario',
    contrasena TEXT
);
""")

# Tabla buses
c.execute("""
CREATE TABLE IF NOT EXISTS buses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT NOT NULL,
    modelo TEXT,
    capacidad INTEGER,
    costo_km REAL
);
""")

# Tabla choferes
c.execute("""
CREATE TABLE IF NOT EXISTS choferes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    cedula TEXT,
    licencia_tipo TEXT,
    fecha_contratacion TEXT
);
""")

# Tabla reservas
c.execute("""
CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    bus_id INTEGER,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    estado TEXT,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY(bus_id) REFERENCES buses(id)
);
""")

conn.commit()
conn.close()
print("Tablas creadas correctamente.")
